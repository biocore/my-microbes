#!/usr/bin/env python
from __future__ import division

__author__ = "John Chase"
__copyright__ = "Copyright 2013, The QIIME project"
__credits__ = ["John Chase", "Greg Caporaso", "Jai Ram Rideout",
               "Yoshiki Vazquez-Baeza"]
__license__ = "GPL"
__version__ = "0.0.0-dev"
__maintainer__ = "John Chase"
__email__ = "jc33@nau.edu"

from collections import defaultdict
from email.Encoders import encode_base64
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.mime.text import MIMEText
from email.Utils import formatdate
from glob import glob
from os import makedirs
from os.path import (abspath, basename, dirname, exists, join, normpath,
                     splitext)
from shutil import copytree, rmtree
from smtplib import SMTP

from cogent.util.misc import remove_files

from numpy import isnan

from qiime.format import format_mapping_file
from qiime.parse import parse_mapping_file, parse_rarefaction
from qiime.pycogent_backports.distribution_plots import generate_box_plots
from qiime.util import (add_filename_suffix, create_dir, MetadataMap,
                        qiime_system_call)
from qiime.workflow import (call_commands_serially, generate_log_fp,
                            no_status_updates, print_commands, print_to_stdout,
                            WorkflowError, WorkflowLogger)

from my_microbes.format import (create_index_html,
        create_alpha_diversity_boxplots_html,
        create_comparative_taxa_plots_html,
        create_otu_category_significance_html,
        format_otu_category_significance_tables_as_html,
        get_personalized_notification_email_text,
        notification_email_subject)
from my_microbes.parse import parse_email_settings, parse_recipients

def get_personal_ids(mapping_data, personal_id_index):
    """Returns a set of personal IDs from a mapping file."""
    return set([line[personal_id_index] for line in mapping_data])

def create_personal_mapping_file(mapping_data, personal_id_of_interest,
                                 personal_id_index, bodysite_index,
                                 individual_titles=None):
    """Creates mapping file on a per-individual basis.

    Inserts new column designating self versus other.
    """
    if individual_titles == None:
        individual_titles = ['Self', 'Other']
    else:
        # Make sure we were given exactly two (distinct) values.
        if len(individual_titles) != 2 or len(set(individual_titles)) != 2:
            raise ValueError("Must provide exactly two distinct values for "
                             "individual titles (e.g. 'Self' and 'Other').")

    site_id_indices = [personal_id_index, bodysite_index]

    personal_map = []
    for line in mapping_data:
        if line[personal_id_index] == personal_id_of_interest:
            individual_title = individual_titles[0]
        else:
            individual_title = individual_titles[1]
        # append the individual title and the site_id values before the last
        # column to conserve the mapping file in a QIIME compliant format
        personal_map.append(line[:-1] + [individual_title] +\
            ['.'.join([line[index] for index in site_id_indices])] + [line[-1]])
    return personal_map

def create_personal_results(output_dir,
                            mapping_fp,
                            coord_fp,
                            collated_dir,
                            otu_table_fp,
                            prefs_fp,
                            personal_id_column,
                            personal_ids=None,
                            column_title='Self',
                            individual_titles=None,
                            category_to_split='BodySite',
                            time_series_category='WeeksSinceStart',
                            rarefaction_depth=10000,
                            alpha=0.05,
                            retain_raw_data=False,
                            suppress_alpha_rarefaction=False,
                            suppress_beta_diversity=False,
                            suppress_taxa_summary_plots=False,
                            suppress_alpha_diversity_boxplots=False,
                            suppress_otu_category_significance=False,
                            command_handler=call_commands_serially,
                            status_update_callback=no_status_updates):
    # Create our output directory and copy over the resources the personalized
    # pages need (e.g. javascript, images, etc.).
    create_dir(output_dir)

    support_files_dir = join(output_dir, 'support_files')
    if not exists(support_files_dir):
        copytree(join(get_project_dir(), 'my_microbes', 'support_files'),
                 support_files_dir)

    logger = WorkflowLogger(generate_log_fp(output_dir))

    mapping_data, header, comments = parse_mapping_file(open(mapping_fp, 'U'))
    try:
        personal_id_index = header.index(personal_id_column)
    except ValueError:
        raise ValueError("Personal ID field '%s' is not a mapping file column "
                         "header." % personal_id_column)
    try:
        bodysite_index = header.index(category_to_split)
    except ValueError:
        raise ValueError("Category to split field '%s' is not a mapping file "
            "column header." % category_to_split)

    header = header[:-1] + [column_title] + [header[-1]]

    # column that differentiates between body-sites within a single individual
    # used for the creation of the vectors in make_3d_plots.py, this data is
    # created by concatenating the two columns when writing the mapping file
    site_id_category = '%s&&%s' % (personal_id_column, category_to_split)
    header.insert(len(header)-1, site_id_category)

    all_personal_ids = get_personal_ids(mapping_data, personal_id_index)
    if personal_ids == None: 
        personal_ids = all_personal_ids
    else:
        for pid in personal_ids:
            if pid not in all_personal_ids:
                raise ValueError("'%s' is not a personal ID in the mapping "
                                 "file column '%s'." %
                                 (pid, personal_id_column))

    if time_series_category not in header:
        raise ValueError("Time series field '%s' is not a mapping file column "
                         "header." % time_series_category)

    otu_table_title = splitext(basename(otu_table_fp))

    output_directories = []
    raw_data_files = []
    raw_data_dirs = []

    # Rarefy the OTU table and split by body site here (instead of on a
    # per-individual basis) as we can use the same rarefied and split tables
    # for each individual.
    if not suppress_otu_category_significance:
        rarefied_otu_table_fp = join(output_dir,
                add_filename_suffix(otu_table_fp,
                                    '_even%d' % rarefaction_depth))

        commands = []
        cmd_title = 'Rarefying OTU table'
        cmd = 'single_rarefaction.py -i %s -o %s -d %s' % (otu_table_fp,
                rarefied_otu_table_fp, rarefaction_depth)
        commands.append([(cmd_title, cmd)])
        raw_data_files.append(rarefied_otu_table_fp)

        per_body_site_dir = join(output_dir, 'per_body_site_otu_tables')

        cmd_title = 'Splitting rarefied OTU table by body site'
        cmd = 'split_otu_table.py -i %s -m %s -f %s -o %s' % (
                rarefied_otu_table_fp, mapping_fp, category_to_split,
                per_body_site_dir)
        commands.append([(cmd_title, cmd)])
        raw_data_dirs.append(per_body_site_dir)

        command_handler(commands, status_update_callback, logger,
                        close_logger_on_success=False)

    for person_of_interest in personal_ids:
        create_dir(join(output_dir, person_of_interest))

        personal_mapping_file_fp = join(output_dir, person_of_interest,
                                        'mapping_file.txt')
        html_fp = join(output_dir, person_of_interest, 'index.html')

        personal_mapping_data = create_personal_mapping_file(mapping_data,
                person_of_interest, personal_id_index, bodysite_index,
                individual_titles)

        personal_mapping_f = open(personal_mapping_file_fp, 'w')
        personal_mapping_f.write(
                format_mapping_file(header, personal_mapping_data, comments))
        personal_mapping_f.close()
        raw_data_files.append(personal_mapping_file_fp)

        column_title_index = header.index(column_title)
        column_title_values = set([e[column_title_index]
                                   for e in personal_mapping_data])
        cat_index = header.index(category_to_split)
        cat_values = set([e[cat_index] for e in personal_mapping_data])

        # Generate alpha diversity boxplots, split by body site, one per
        # metric. We run this one first because it completes relatively
        # quickly and it does not call any QIIME scripts.
        alpha_diversity_boxplots_html = ''
        if not suppress_alpha_diversity_boxplots:
            adiv_boxplots_dir = join(output_dir, person_of_interest,
                                     'adiv_boxplots')
            create_dir(adiv_boxplots_dir)
            output_directories.append(adiv_boxplots_dir)

            logger.write("\nGenerating alpha diversity boxplots (%s)\n\n" %
                         person_of_interest)

            plot_filenames = _generate_alpha_diversity_boxplots(
                    collated_dir, personal_mapping_file_fp,
                    category_to_split, column_title, rarefaction_depth,
                    adiv_boxplots_dir)

            # Create relative paths for use with the index page.
            rel_boxplot_dir = basename(normpath(adiv_boxplots_dir))
            plot_fps = [join(rel_boxplot_dir, plot_filename)
                        for plot_filename in plot_filenames]

            alpha_diversity_boxplots_html = \
                    create_alpha_diversity_boxplots_html(plot_fps)

        ## Alpha rarefaction steps
        if not suppress_alpha_rarefaction:
            rarefaction_dir = join(output_dir, person_of_interest,
                                   'alpha_rarefaction')
            output_directories.append(rarefaction_dir)

            commands = []
            cmd_title = 'Creating rarefaction plots (%s)' % person_of_interest
            cmd = 'make_rarefaction_plots.py -i %s -m %s -p %s -o %s' % (
                    collated_dir, personal_mapping_file_fp, prefs_fp,
                    rarefaction_dir)
            commands.append([(cmd_title, cmd)])

            raw_data_dirs.append(join(rarefaction_dir, 'average_plots'))
            raw_data_dirs.append(join(rarefaction_dir, 'average_tables'))

            command_handler(commands, status_update_callback, logger,
                            close_logger_on_success=False)

        ## Beta diversity steps
        if not suppress_beta_diversity:
            pcoa_dir = join(output_dir, person_of_interest, 'beta_diversity')
            output_directories.append(pcoa_dir)

            commands = []
            cmd_title = 'Creating beta diversity plots (%s)' % \
                        person_of_interest
            cmd = 'make_3d_plots.py -m %s -p %s -i %s -o %s --custom_axes=' % (
                personal_mapping_file_fp, prefs_fp, coord_fp, pcoa_dir) +\
                '\'%s\' --add_vectors=\'%s,%s\'' % (time_series_category,
                site_id_category, time_series_category)
            commands.append([(cmd_title, cmd)])

            command_handler(commands, status_update_callback, logger,
                            close_logger_on_success=False)

        ## Time series taxa summary plots steps
        if not suppress_taxa_summary_plots:
            area_plots_dir = join(output_dir, person_of_interest, 'time_series')
            create_dir(area_plots_dir)
            output_directories.append(area_plots_dir)

            ## Split OTU table into self/other per-body-site tables
            commands = []
            cmd_title = 'Splitting OTU table into self/other (%s)' % \
                        person_of_interest
            cmd = 'split_otu_table.py -i %s -m %s -f %s -o %s' % (otu_table_fp,
                    personal_mapping_file_fp, column_title, area_plots_dir)
            commands.append([(cmd_title, cmd)])

            command_handler(commands, status_update_callback, logger,
                            close_logger_on_success=False)

            for column_title_value in column_title_values:
                biom_fp = join(area_plots_dir,
                               add_filename_suffix(otu_table_fp,
                                                   '_%s' % column_title_value))
                column_title_map_fp = join(area_plots_dir, 'mapping_%s.txt' %
                                                           column_title_value)
                raw_data_files.append(biom_fp)
                raw_data_files.append(column_title_map_fp)

                body_site_dir = join(area_plots_dir, column_title_value)

                commands = []
                cmd_title = 'Splitting "%s" OTU table by body site (%s)' % \
                            (column_title_value, person_of_interest)
                cmd = 'split_otu_table.py -i %s -m %s -f %s -o %s' % (biom_fp,
                        personal_mapping_file_fp, category_to_split,
                        body_site_dir)
                commands.append([(cmd_title, cmd)])
                raw_data_dirs.append(body_site_dir)

                command_handler(commands, status_update_callback, logger,
                                close_logger_on_success=False)

                commands = []
                for cat_value in cat_values:
                    body_site_otu_table_fp = join(body_site_dir,
                            add_filename_suffix(biom_fp, '_%s' % cat_value))

                    # We won't always get an OTU table if the mapping file
                    # category contains samples that aren't in the OTU table
                    # (e.g. the 'na' state for body site).
                    if exists(body_site_otu_table_fp):
                        plots = join(area_plots_dir, 'taxa_plots_%s_%s' % (
                            column_title_value, cat_value))

                        cmd_title = 'Creating taxa summary plots (%s)' % \
                                    person_of_interest
                        cmd = ('summarize_taxa_through_plots.py -i %s '
                               '-o %s -c %s -m %s -s' %
                               (body_site_otu_table_fp, plots,
                                time_series_category,
                                personal_mapping_file_fp))
                        commands.append([(cmd_title, cmd)])

                        raw_data_files.append(join(plots, '*.biom'))
                        raw_data_files.append(join(plots, '*.txt'))

                        create_comparative_taxa_plots_html(cat_value, 
                                join(area_plots_dir, '%s_comparative.html' %
                                                     cat_value))

                command_handler(commands, status_update_callback, logger,
                                close_logger_on_success=False)

        # Generate OTU category significance tables (per body site).
        otu_cat_sig_output_fps = []
        otu_category_significance_html = ''
        if not suppress_otu_category_significance:
            otu_cat_sig_dir = join(output_dir, person_of_interest,
                                   'otu_category_significance')
            create_dir(otu_cat_sig_dir)
            output_directories.append(otu_cat_sig_dir)

            # For each body-site rarefied OTU table, run
            # otu_category_significance.py using self versus other category.
            # Keep track of each output file that is created because we need to
            # parse these later on.
            commands = []
            for cat_value in cat_values:
                body_site_otu_table_fp = join(per_body_site_dir,
                        add_filename_suffix(rarefied_otu_table_fp,
                                            '_%s' % cat_value))

                if exists(body_site_otu_table_fp):
                    body_site_map_fp = join(per_body_site_dir,
                                            'mapping_%s.txt' % cat_value)
                    otu_cat_output_fp = join(otu_cat_sig_dir,
                                             'otu_cat_sig_%s.txt' % cat_value)

                    cmd_title = ('Testing for significant differences in '
                                 'OTU abundances in "%s" body site (%s)' % (
                                 cat_value, person_of_interest))
                    cmd = ('otu_category_significance.py -i %s -m %s -c %s '
                           '-o %s' % (body_site_otu_table_fp, body_site_map_fp,
                                      column_title, otu_cat_output_fp))
                    commands.append([(cmd_title, cmd)])
                    raw_data_files.append(otu_cat_output_fp)
                    otu_cat_sig_output_fps.append(otu_cat_output_fp)

            command_handler(commands, status_update_callback, logger,
                            close_logger_on_success=False)

            # Reformat otu category significance tables.
            otu_cat_sig_html_filenames = \
                    format_otu_category_significance_tables_as_html(
                            otu_cat_sig_output_fps, alpha, otu_cat_sig_dir, 
                            individual_titles)

            # Create relative paths for use with the index page.
            rel_otu_cat_sig_dir = basename(normpath(otu_cat_sig_dir))
            otu_cat_sig_html_fps = [join(rel_otu_cat_sig_dir, html_filename)
                    for html_filename in otu_cat_sig_html_filenames]

            otu_category_significance_html = \
                    create_otu_category_significance_html(otu_cat_sig_html_fps)

        # Create the index.html file for the current individual.
        create_index_html(person_of_interest, html_fp,
                alpha_diversity_boxplots_html=alpha_diversity_boxplots_html,
                otu_category_significance_html=otu_category_significance_html)

    logger.close()

    # Clean up the unnecessary raw data files and directories. glob will only
    # grab paths that exist.
    if not retain_raw_data:
        for raw_data_fp_glob in raw_data_files:
            remove_files(glob(raw_data_fp_glob))

        for raw_data_dir_glob in raw_data_dirs:
            for dir_to_remove in glob(raw_data_dir_glob):
                rmtree(dir_to_remove)

    return output_directories

def get_project_dir():
    """Returns the top-level personal microbiome delivery system directory.

    Taken from QIIME's (https://github.com/qiime/qiime)
    qiime.util.get_qiime_project_dir.
    """
    # Get the full path of util.py
    current_file_path = abspath(__file__)
    # Get the directory containing util.py
    current_dir_path = dirname(current_file_path)
    # Return the directory containing the directory containing util.py
    return dirname(current_dir_path)

def _generate_alpha_diversity_boxplots(collated_adiv_dir, map_fp,
                                       split_category, comparison_category,
                                       rarefaction_depth, output_dir):
    """Generates per-body-site self vs. other alpha diversity boxplots.

    Creates a plot for each input collated alpha diversity file (i.e. metric)
    in collated_adiv_dir. Returns a list of plot filenames that were created in
    output_dir.

    Arguments:
        collated_adiv_dir - path to directory containing one or more collated
            alpha diversity files
        map_fp - filepath to metadata mapping file
        split_category - category to split on, e.g. body site. A boxplot will
            be created for each category value (e.g. tongue, palm, etc.)
        comparison_category - category to split on within each of the split
            categories (e.g. self, other)
        rarefaction_depth - rarefaction depth to use when pulling data from
            rarefaction files
        output_dir - directory to write output plot images to
    """
    metadata_map = MetadataMap.parseMetadataMap(open(map_fp, 'U'))
    collated_adiv_fps = glob(join(collated_adiv_dir, '*.txt'))
    plot_title = 'Alpha diversity (%d seqs/sample)' % rarefaction_depth

    # Generate a plot for each collated alpha diversity metric file.
    created_files = []
    for collated_adiv_fp in collated_adiv_fps:
        adiv_metric = splitext(basename(collated_adiv_fp))[0]

        x_tick_labels, dists = _collect_alpha_diversity_boxplot_data(
                open(collated_adiv_fp, 'U'), metadata_map, rarefaction_depth,
                split_category, comparison_category)

        plot_figure = generate_box_plots(dists,
                                         x_tick_labels=x_tick_labels,
                                         title=plot_title,
                                         x_label='Grouping',
                                         y_label=adiv_metric)
        plot_fp = join(output_dir, '%s.png' % adiv_metric)
        plot_figure.savefig(plot_fp)
        created_files.append(basename(plot_fp))

    return created_files

def _collect_alpha_diversity_boxplot_data(rarefaction_f, metadata_map,
                                          rarefaction_depth, split_category,
                                          comparison_category):
    """Pulls data from rarefaction file based on supplied categories."""
    # Pull out rarefaction data for the specified depth.
    rarefaction = parse_rarefaction(rarefaction_f)

    # First three vals are part of the header, so ignore them.
    sample_ids = rarefaction[0][3:]

    # First two vals are depth and iteration number, so ignore them.
    rarefaction_data = [row[2:] for row in rarefaction[3]
                        if row[0] == rarefaction_depth]

    if not rarefaction_data:
        raise ValueError("Rarefaction depth of %d could not be found in "
                         "collated alpha diversity file." % rarefaction_depth)

    # Build up dict mapping (body site, [self|other]) -> distribution.
    plot_data = defaultdict(list)
    for row in rarefaction_data:
        assert len(sample_ids) == len(row)
        for sample_id, adiv_val in zip(sample_ids, row):
            if not isnan(adiv_val):
                split_cat_val = metadata_map.getCategoryValue(sample_id,
                                                              split_category)
                comp_cat_val = metadata_map.getCategoryValue(sample_id,
                        comparison_category)

                plot_data[split_cat_val, comp_cat_val].append(adiv_val)

    # Format tick labels as '<body site> (self|other)' and sort alphabetically.
    plot_data = sorted(map(lambda e: ('%s (%s)' %
                                      (e[0][0], e[0][1]), e[1]),
                           plot_data.items()))
    x_tick_labels = []
    dists = []
    for label, dist in plot_data:
        x_tick_labels.append(label)
        dists.append(dist)

    return x_tick_labels, dists

def notify_participants(recipients_f, email_settings_f, dry_run=True):
    """Sends an email to each participant in the study.

    Arguments:
        recipients_f - file containing email recipients (see
            parse.parse_recipients for more details)
        email_settings_f - file containing settings for sending emails (see
            parse.parse_email_settings for more details)
        dry_run - if True, no emails are sent and information of what would
            have been done is printed to stdout. If False, no output is printed
            and emails are sent
    """
    recipients = parse_recipients(recipients_f)
    email_settings = parse_email_settings(email_settings_f)

    sender = email_settings['sender']
    password = email_settings['password']
    server = email_settings['smtp_server']
    port = email_settings['smtp_port']

    if dry_run:
        num_recipients = len(recipients)

        print("Running script in dry-run mode. No emails will be sent. Here's "
              "what I would have done:\n")
        print("Sender information:\n\nFrom address: %s\nPassword: %s\nSMTP "
              "server: %s\nPort: %s\n" % (sender, password, server, port))
        print "Sending emails to %d recipient(s)." % num_recipients

        if num_recipients > 0:
            # Sort so that we will grab the same recipient each time this is
            # run over the same input files.
            sample_recipient = sorted(recipients.items())[0]

            print "\nSample email:\n"
            print "To: %s" % ', '.join(sample_recipient[1])
            print "From: %s" % sender
            print "Subject: %s" % notification_email_subject
            print "Body:\n%s\n" % get_personalized_notification_email_text(
                    sample_recipient[0])
    else:
        for personal_id, addresses in recipients.items():
            personalized_text = \
                    get_personalized_notification_email_text(personal_id)
            print "Sending email to %s (%s)... " % (personal_id,
                                                    ', '.join(addresses)),
            send_email(server, port, sender, password, addresses,
                       notification_email_subject, personalized_text)
            print "success!"

def send_email(host, port, sender, password, recipients, subject, body,
               attachments=None):
    """Sends an email (optionally with attachments).

    This function does not return anything. It is not unit tested because it
    sends an actual email, and thus is difficult to test.

    This code is largely based on the code found here:
    http://www.blog.pythonlibrary.org/2010/05/14/how-to-send-email-with-python/
    http://segfault.in/2010/12/sending-gmail-from-python/

    Taken from Clout's (https://github.com/qiime/clout) util module.

    Arguments:
        host - the STMP server to send the email with
        port - the port number of the SMTP server to connect to
        sender - the sender email address (i.e. who this message is from). This
            will be used as the username when logging into the SMTP server
        password - the password to log into the SMTP server with
        recipients - a list of email addresses to send the email to
        subject - the subject of the email
        body - the body of the email
        attachments - a list of 2-element tuples, where the first element is
            the filename that will be used for the email attachment (as the
            recipient will see it), and the second element is the file to be
            attached
    """
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    msg['Subject'] = subject
    msg['Date'] = formatdate(localtime=True)
 
    if attachments is not None:
        for attachment_name, attachment_f in attachments:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment_f.read())
            encode_base64(part)
            part.add_header('Content-Disposition',
                            'attachment; filename="%s"' % attachment_name)
            msg.attach(part)
    part = MIMEText('text', 'plain')
    part.set_payload(body)
    msg.attach(part)
 
    server = SMTP(host, port)
    server.ehlo()
    server.starttls()
    server.ehlo
    server.login(sender, password)
    server.sendmail(sender, recipients, msg.as_string())
    server.quit()
