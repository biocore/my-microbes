#!/usr/bin/env python
from __future__ import division

__author__ = "John Chase"
__copyright__ = "Copyright 2013, The QIIME project"
__credits__ = ["John Chase", "Greg Caporaso", "Jai Ram Rideout"]
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
from os.path import basename, exists, join, normpath, splitext
from smtplib import SMTP

from numpy import isnan

from qiime.format import format_mapping_file
from qiime.parse import parse_mapping_file, parse_rarefaction
from qiime.pycogent_backports.distribution_plots import generate_box_plots
from qiime.util import (add_filename_suffix, create_dir, MetadataMap,
                        qiime_system_call)

from personal_microbiome.format import (create_index_html,
        create_alpha_diversity_boxplots_html_table_row,
        create_comparative_taxa_plots_html, notification_email_subject,
        get_personalized_notification_email_text)
from personal_microbiome.parse import parse_email_settings, parse_recipients

def get_personal_ids(mapping_data, personal_id_index):
    result = []
    for i in mapping_data:
        if i[personal_id_index] not in result: 
            result.append(i[personal_id_index]) 
        else: 
            pass
    return result
    
def create_personal_mapping_file(map_as_list,
                                 header, 
                                 comments, 
                                 personal_id_of_interest, 
                                 output_fp, 
                                 personal_id_index, 
                                 individual_titles):
    """ creates mapping file on a per-individual basis """
    if individual_titles == None: 
        individual_titles = ['Self', 'Other']
    else: 
        individual_titles = individual_titles.split(',')   
    personal_map = []
    for line in map_as_list:
        personal_map.append(line[:])
    for i in personal_map:   
        if i[personal_id_index] == personal_id_of_interest: 
            i.append(individual_titles[0])
        else: 
            i.append(individual_titles[1])
    personal_mapping_file = format_mapping_file(header, personal_map, comments) 
    output_f = open(output_fp,'w')
    output_f.write(personal_mapping_file)
    output_f.close()
    return personal_map
    
def create_personal_results(mapping_fp, 
                            distance_matrix_fp, 
                            collated_dir_fp, 
                            output_fp, prefs_fp, 
                            personal_id_field,
                            otu_table,
                            parameter_fp, 
                            personal_ids=None, 
                            column_title='Self', 
                            individual_titles=None,
                            category_to_split='BodySite',
                            time_series_category='WeeksSinceStart',
                            rarefaction_depth=10000,
                            suppress_alpha_rarefaction=False,
                            suppress_beta_diversity=False,
                            suppress_taxa_summary_plots=False,
                            suppress_alpha_diversity_boxplots=False,
                            suppress_otu_category_significance=False,
                            verbose=False):
    map_as_list, header, comments = parse_mapping_file(open(mapping_fp, 'U'))
    try:
        personal_id_index = header.index(personal_id_field)
    except ValueError:
        raise ValueError("personal id field (%s) is not a mapping file column header" %
                         personal_id_field)
    header.append(column_title)
    
    if personal_ids == None: 
        personal_ids  = get_personal_ids(map_as_list, personal_id_index)
    else:
        for id in personal_ids.split(','):
            if id not in get_personal_ids(map_as_list, personal_id_index):
                raise ValueError('%s is not an id in the mapping file.' %id)
        personal_ids = personal_ids.split(',')

    otu_table_title = otu_table.split('/')[-1].split('.')
        
    makedirs(output_fp)
    output_directories = []
    for person_of_interest in personal_ids:
        makedirs(join(output_fp, person_of_interest))

        personal_mapping_file_fp = join(output_fp, person_of_interest,
                                        "mapping_file.txt")
        html_fp = join(output_fp, person_of_interest, "index.html")

        personal_map = create_personal_mapping_file(map_as_list,
                                     header,
                                     comments,
                                     person_of_interest,
                                     personal_mapping_file_fp, 
                                     personal_id_index, 
                                     individual_titles)
        column_title_index = header.index(column_title)
        column_title_values = set([e[column_title_index] for e in personal_map])
        cat_index = header.index(category_to_split)
        cat_values = set([e[cat_index] for e in personal_map])
        
        ## Alpha rarefaction steps
        if not suppress_alpha_rarefaction:
            rarefaction_dir = join(output_fp, person_of_interest, "alpha_rarefaction")
            output_directories.append(rarefaction_dir)

            cmd = "make_rarefaction_plots.py -i %s -m %s -p %s -o %s" % (collated_dir_fp, 
                                                                         personal_mapping_file_fp,
                                                                         prefs_fp, 
                                                                         rarefaction_dir)
            if verbose:
                print cmd          
            stdout, stderr, return_code = qiime_system_call(cmd)
            if return_code != 0:
                raise ValueError("Command failed!\nCommand: %s\n Stdout: %s\n Stderr: %s\n" %\
                (cmd, stdout, stderr))
        
        ## Beta diversity steps
        if not suppress_beta_diversity:
            pcoa_dir = join(output_fp, person_of_interest, "beta_diversity")
            output_directories.append(pcoa_dir)

            cmd = "make_3d_plots.py -m %s -p %s -i %s -o %s" % (personal_mapping_file_fp, 
                                                                prefs_fp, 
                                                                distance_matrix_fp, 
                                                                pcoa_dir)
            if verbose:
                print cmd
            stdout, stderr, return_code = qiime_system_call(cmd)
            if return_code != 0:
                raise ValueError("Command failed!\nCommand: %s\n Stdout: %s\n Stderr: %s\n" %\
                (cmd, stdout, stderr))
        
        ## Split OTU table into self/other per-body-site tables
        if not suppress_taxa_summary_plots:
            area_plots_dir = join(output_fp, person_of_interest, "time_series")
            output_directories.append(area_plots_dir)

            cmd = "split_otu_table.py -i %s -m %s -f %s -o %s" % (otu_table,
                                                                  personal_mapping_file_fp,
                                                                  column_title, 
                                                                  area_plots_dir)
            if verbose:
                print cmd
            stdout, stderr, return_code = qiime_system_call(cmd)
            if return_code != 0:
                raise ValueError("Command failed!\nCommand: %s\n Stdout: %s\n Stderr: %s\n" %\
                (cmd, stdout, stderr))
                
            
            for column_title_value in column_title_values:
                print column_title_value
                biom_fp = join(area_plots_dir, '%s_%s.%s' % (otu_table_title[0], column_title_value, otu_table_title[1]))
                body_site_dir = join(area_plots_dir, column_title_value)
                cmd = "split_otu_table.py -i %s -m %s -f %s -o %s" % (biom_fp,
                                                                      personal_mapping_file_fp,
                                                                      category_to_split, 
                                                                      body_site_dir)
                if verbose:
                    print cmd
                stdout, stderr, return_code = qiime_system_call(cmd)
                if return_code != 0:
                    raise ValueError("Command failed!\nCommand: %s\n Stdout: %s\n Stderr: %s\n" %\
                    (cmd, stdout, stderr))
                    
                for cat_value in cat_values:
                    otu_table_fp = join(body_site_dir, "otu_table_%s_%s.biom" % (column_title_value, cat_value))
                    print otu_table_fp
                    if exists(otu_table_fp):
                        # Not supporting parameter files yet
                        #if parameter_fp == None:
                        #    parameter_fp = ''
                        #else:
                        #    parameter_fp = '-p %s' %parameter_fp
                        plots = join(area_plots_dir, "taxa_plots_%s_%s" % (column_title_value, cat_value))
                        cmd = "summarize_taxa_through_plots.py -i %s -o %s -c %s -m %s -s" % (otu_table_fp,
                                                                                                    plots,
                                                                                                    time_series_category, 
                                                                                                    personal_mapping_file_fp)
                                                                                                    #parameter_fp)
                        if verbose:
                            print cmd
                        stdout, stderr, return_code = qiime_system_call(cmd)
                        if return_code != 0:
                            raise ValueError("Command failed!\nCommand: %s\n Stdout: %s\n Stderr: %s\n" %\
                            (cmd, stdout, stderr))
                        create_comparative_taxa_plots_html(cat_value, 
                                                           join(area_plots_dir,'%s_comparative.html' % cat_value))
        
        # Generate alpha diversity boxplots, split by body site, one per
        # metric.
        alpha_diversity_boxplots_html = ''
        if not suppress_alpha_diversity_boxplots:
            adiv_boxplots_dir = join(output_fp, person_of_interest,
                                     "adiv_boxplots")
            create_dir(adiv_boxplots_dir, fail_on_exist=True)
            output_directories.append(adiv_boxplots_dir)

            if verbose:
                print "Generating alpha diversity boxplots."

            plot_filenames = _generate_alpha_diversity_boxplots(
                    collated_dir_fp, personal_mapping_file_fp,
                    category_to_split, column_title, rarefaction_depth,
                    adiv_boxplots_dir)

            # Create relative paths for use with the index page.
            rel_boxplot_dir = basename(normpath(adiv_boxplots_dir))
            plot_fps = [join(rel_boxplot_dir, plot_filename)
                        for plot_filename in plot_filenames]

            alpha_diversity_boxplots_html = \
                    create_alpha_diversity_boxplots_html_table_row(plot_fps)

        # Generate OTU category significance tables (per body site).
        if not suppress_otu_category_significance:
            otu_cat_sig_dir = join(output_fp, person_of_interest,
                                   'otu_category_significance')
            create_dir(otu_cat_sig_dir, fail_on_exist=True)
            output_directories.append(otu_cat_sig_dir)

            rarefied_otu_table_fp = join(otu_cat_sig_dir,
                    add_filename_suffix(otu_table,
                                        '_even%d' % rarefaction_depth))

            # Rarefy OTU table (based on otu_category_significance.py
            # recommendataion).
            cmd = 'single_rarefaction.py -i %s -o %s -d %s' % (otu_table,
                    rarefied_otu_table_fp, rarefaction_depth)
            if verbose:
                print cmd
            stdout, stderr, return_code = qiime_system_call(cmd)
            if return_code != 0:
                raise ValueError("Command failed!\nCommand: %s\n Stdout: %s\n Stderr: %s\n" %\
                (cmd, stdout, stderr))

            # Split OTU table into per-body-site tables.
            cmd = 'split_otu_table.py -i %s -m %s -f %s -o %s' % (
                    rarefied_otu_table_fp, personal_mapping_file_fp,
                    category_to_split, otu_cat_sig_dir)
            if verbose:
                print cmd
            stdout, stderr, return_code = qiime_system_call(cmd)
            if return_code != 0:
                raise ValueError("Command failed!\nCommand: %s\n Stdout: %s\n Stderr: %s\n" %\
                (cmd, stdout, stderr))

            # For each body-site OTU table, run otu_category_significance.py
            # using self versus other category.
            for cat_value in cat_values:
                body_site_otu_table_fp = join(otu_cat_sig_dir,
                        add_filename_suffix(rarefied_otu_table_fp,
                                            '_%s' % cat_value))
                otu_cat_output_fp = join(otu_cat_sig_dir,
                                         'otu_cat_sig_%s.txt' % cat_value)

                cmd = 'otu_category_significance.py -i %s -m %s -c %s -o %s' % (
                        body_site_otu_table_fp, personal_mapping_file_fp,
                        column_title, otu_cat_output_fp)
                if verbose:
                    print cmd
                stdout, stderr, return_code = qiime_system_call(cmd)
                if return_code != 0:
                    raise ValueError("Command failed!\nCommand: %s\n Stdout: %s\n Stderr: %s\n" %\
                    (cmd, stdout, stderr))

        # Create the index.html file for the current individual.
        create_index_html(person_of_interest, html_fp,
                alpha_diversity_boxplots_html=alpha_diversity_boxplots_html)

    return output_directories

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
