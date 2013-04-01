#!/usr/bin/env python
from __future__ import division

__author__ = "John Chase"
__copyright__ = "Copyright 2013, The QIIME project"
__credits__ = ["John Chase", "Greg Caporaso", "Jai Ram Rideout",
               "Yoshiki Vazquez-Baeza"]
__license__ = "GPL"
__version__ = "0.1.0-dev"
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
from random import choice, randint
from shutil import copytree, rmtree
from smtplib import SMTP
from string import digits, letters

from biom.parse import parse_biom_table

from cogent.util.misc import remove_files

from numpy import isnan

from qiime.format import format_mapping_file
from qiime.parse import parse_mapping_file, parse_rarefaction
from qiime.pycogent_backports.distribution_plots import generate_box_plots
from qiime.util import (add_filename_suffix, create_dir, MetadataMap,
                        qiime_system_call)
from qiime.workflow.util import (call_commands_serially, generate_log_fp,
                            no_status_updates, print_commands, print_to_stdout,
                            WorkflowError, WorkflowLogger)

from my_microbes.format import (create_index_html,
        create_alpha_diversity_boxplots_html,
        create_comparative_taxa_plots_html,
        create_otu_category_significance_html,
        create_otu_category_significance_html_tables,
        create_taxa_summary_plots_html,
        format_htaccess_file,
        format_title,
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
                            rep_set_fp=None,
                            body_site_rarefied_otu_table_dir=None,
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

        if body_site_rarefied_otu_table_dir is None:
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
        else:
            per_body_site_dir = body_site_rarefied_otu_table_dir

    for person_of_interest in personal_ids:
        # Files to clean up on a per-individual basis.
        personal_raw_data_files = []
        personal_raw_data_dirs = []

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
        personal_raw_data_files.append(personal_mapping_file_fp)

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

            personal_raw_data_dirs.append(join(rarefaction_dir,
                                               'average_plots'))
            personal_raw_data_dirs.append(join(rarefaction_dir,
                                               'average_tables'))

            command_handler(commands, status_update_callback, logger,
                            close_logger_on_success=False)

        ## Beta diversity steps
        if not suppress_beta_diversity:
            pcoa_dir = join(output_dir, person_of_interest, 'beta_diversity')
            pcoa_time_series_dir = join(output_dir, person_of_interest, 
                                         'beta_diversity_time_series')
            output_directories.append(pcoa_dir)
            output_directories.append(pcoa_time_series_dir)

            commands = []
            cmd_title = 'Creating beta diversity time series plots (%s)' % \
                        person_of_interest
            cmd = 'make_3d_plots.py -m %s -p %s -i %s -o %s --custom_axes=' % (
                personal_mapping_file_fp, prefs_fp, coord_fp, pcoa_time_series_dir) +\
                '\'%s\' --add_vectors=\'%s,%s\'' % (time_series_category,
                site_id_category, time_series_category)
            commands.append([(cmd_title, cmd)])
            
            cmd_title = 'Creating beta diversity plots (%s)' % \
                        person_of_interest
            cmd = 'make_3d_plots.py  -m %s -p %s -i %s -o %s' % (personal_mapping_file_fp,
                                                                 prefs_fp, coord_fp, 
                                                                 pcoa_dir)
            commands.append([(cmd_title, cmd)])

            command_handler(commands, status_update_callback, logger,
                            close_logger_on_success=False)

        ## Time series taxa summary plots steps
        taxa_summary_plots_html = ''
        if not suppress_taxa_summary_plots:
            area_plots_dir = join(output_dir, person_of_interest,
                                  'time_series')
            create_dir(area_plots_dir)
            output_directories.append(area_plots_dir)

            files_to_remove, dirs_to_remove = _generate_taxa_summary_plots(
                    otu_table_fp, personal_mapping_file_fp, person_of_interest,
                    column_title, column_title_values, category_to_split,
                    cat_values, time_series_category, area_plots_dir,
                    command_handler, status_update_callback, logger)

            personal_raw_data_files.extend(files_to_remove)
            personal_raw_data_dirs.extend(dirs_to_remove)

            taxa_summary_plots_html = create_taxa_summary_plots_html(
                    output_dir, person_of_interest, cat_values)

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
            valid_body_sites = []
            for cat_value in cat_values:
                body_site_otu_table_fp = join(per_body_site_dir,
                        add_filename_suffix(rarefied_otu_table_fp,
                                            '_%s' % cat_value))

                if exists(body_site_otu_table_fp):
                    # Make sure we have at least one sample for Self, otherwise
                    # otu_category_significance.py crashes with a division by
                    # zero error.
                    body_site_otu_table_f = open(body_site_otu_table_fp, 'U')
                    personal_mapping_file_f = open(personal_mapping_file_fp,
                                                   'U')
                    personal_sample_count = _count_per_individual_samples(
                            body_site_otu_table_f, personal_mapping_file_f,
                            personal_id_column, person_of_interest)
                    body_site_otu_table_f.close()
                    personal_mapping_file_f.close()

                    if personal_sample_count < 1:
                        continue
                    else:
                        valid_body_sites.append(cat_value)

                    otu_cat_output_fp = join(otu_cat_sig_dir,
                                             'otu_cat_sig_%s.txt' % cat_value)

                    cmd_title = ('Testing for significant differences in '
                                 'OTU abundances in "%s" body site (%s)' % (
                                 cat_value, person_of_interest))
                    cmd = ('otu_category_significance.py -i %s -m %s -c %s '
                           '-o %s' % (body_site_otu_table_fp,
                                      personal_mapping_file_fp,
                                      column_title,
                                      otu_cat_output_fp))
                    commands.append([(cmd_title, cmd)])

                    personal_raw_data_files.append(otu_cat_output_fp)
                    otu_cat_sig_output_fps.append(otu_cat_output_fp)

            # Hack to allow print-only mode.
            if command_handler is not print_commands and not valid_body_sites:
                raise ValueError("None of the body sites for personal ID '%s' "
                                 "could be processed because there were no "
                                 "matching samples in the rarefied OTU table."
                                 % person_of_interest)

            command_handler(commands, status_update_callback, logger,
                            close_logger_on_success=False)

            # Reformat otu category significance tables.
            otu_cat_sig_html_filenames = \
                    create_otu_category_significance_html_tables(
                            otu_cat_sig_output_fps, alpha, otu_cat_sig_dir, 
                            individual_titles, rep_set_fp=rep_set_fp)

            # Create relative paths for use with the index page.
            rel_otu_cat_sig_dir = basename(normpath(otu_cat_sig_dir))
            otu_cat_sig_html_fps = [join(rel_otu_cat_sig_dir, html_filename)
                    for html_filename in otu_cat_sig_html_filenames]

            otu_category_significance_html = \
                    create_otu_category_significance_html(otu_cat_sig_html_fps)

        # Create the index.html file for the current individual.
        create_index_html(person_of_interest, html_fp,
                taxa_summary_plots_html=taxa_summary_plots_html,
                alpha_diversity_boxplots_html=alpha_diversity_boxplots_html,
                otu_category_significance_html=otu_category_significance_html)

        # Clean up the unnecessary raw data files and directories for the
        # current individual. glob will only grab paths that exist.
        if not retain_raw_data:
            clean_up_raw_data_files(personal_raw_data_files,
                                    personal_raw_data_dirs)


    # Clean up any remaining raw data files that weren't created on a
    # per-individual basis.
    if not retain_raw_data:
        clean_up_raw_data_files(raw_data_files, raw_data_dirs)

    logger.close()

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

def clean_up_raw_data_files(raw_data_files, raw_data_dirs):
    for raw_data_fp_glob in raw_data_files:
        remove_files(glob(raw_data_fp_glob))

    for raw_data_dir_glob in raw_data_dirs:
        for dir_to_remove in glob(raw_data_dir_glob):
            rmtree(dir_to_remove)

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
                                         y_label=format_title(adiv_metric))
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

def _generate_taxa_summary_plots(otu_table_fp, personal_map_fp, personal_id,
        personal_cat, personal_cat_values, body_site_cat, body_site_cat_values,
        time_series_cat, output_dir, command_handler, status_update_callback,
        logger):
    files_to_remove = []
    dirs_to_remove = []

    ## Split OTU table into self/other per-body-site tables
    commands = []
    cmd_title = 'Splitting OTU table into self/other (%s)' % personal_id
    cmd = 'split_otu_table.py -i %s -m %s -f %s -o %s' % (otu_table_fp,
            personal_map_fp, personal_cat, output_dir)
    commands.append([(cmd_title, cmd)])

    command_handler(commands, status_update_callback, logger,
                    close_logger_on_success=False)

    # Prefix to be used for taxa summary dirs. Will be
    # <taxa_summary_dir_prefix>_<self|other>_<body site>/.
    ts_dir_prefix = 'taxa_summaries'

    # Create taxa summaries for self and other, per body site.
    for personal_cat_value in personal_cat_values:
        personal_cat_biom_fp = join(output_dir,
                add_filename_suffix(otu_table_fp, '_%s' % personal_cat_value))
        personal_cat_map_fp = join(output_dir,
                                   'mapping_%s.txt' % personal_cat_value)
        files_to_remove.append(personal_cat_biom_fp)
        files_to_remove.append(personal_cat_map_fp)

        body_site_dir = join(output_dir, personal_cat_value)

        commands = []
        cmd_title = 'Splitting "%s" OTU table by body site (%s)' % (
                personal_cat_value, personal_id)
        cmd = 'split_otu_table.py -i %s -m %s -f %s -o %s' % (
                personal_cat_biom_fp, personal_map_fp, body_site_cat,
                body_site_dir)
        commands.append([(cmd_title, cmd)])
        dirs_to_remove.append(body_site_dir)

        command_handler(commands, status_update_callback, logger,
                        close_logger_on_success=False)

        commands = []
        for body_site_cat_value in body_site_cat_values:
            body_site_otu_table_fp = join(body_site_dir,
                    add_filename_suffix(personal_cat_biom_fp,
                                        '_%s' % body_site_cat_value))

            # We won't always get an OTU table if the mapping file
            # category contains samples that aren't in the OTU table
            # (e.g. the 'na' state for body site).
            if exists(body_site_otu_table_fp):
                ts_dir = join(output_dir, '%s_%s_%s' % (ts_dir_prefix,
                    personal_cat_value, body_site_cat_value))
                create_dir(ts_dir)
                dirs_to_remove.append(ts_dir)

                # Summarize.
                summarized_otu_table_fp = join(ts_dir,
                        '%s_otu_table.biom' % time_series_cat)

                cmd_title = ('Summarizing OTU table by category (%s)' %
                             personal_id)
                cmd = ('summarize_otu_by_cat.py -i %s -c %s -o %s '
                       '-m %s ' % (personal_map_fp, body_site_otu_table_fp,
                        summarized_otu_table_fp, time_series_cat))
                commands.append([(cmd_title, cmd)])

                # Sort.
                sorted_otu_table_fp = join(ts_dir,
                        '%s_otu_table_sorted.biom' % time_series_cat)

                cmd_title = 'Sorting OTU table (%s)' % personal_id
                cmd = ('sort_otu_table.py -i %s -o %s' % (
                       summarized_otu_table_fp, sorted_otu_table_fp))
                commands.append([(cmd_title, cmd)])

                # Summarize taxa.
                cmd_title = 'Summarizing taxa (%s)' % personal_id
                cmd = ('summarize_taxa.py -i %s -o %s' % (
                    sorted_otu_table_fp, ts_dir))
                commands.append([(cmd_title, cmd)])

                create_comparative_taxa_plots_html(body_site_cat_value,
                        join(output_dir,
                             '%s_comparative.html' % body_site_cat_value))

        command_handler(commands, status_update_callback, logger,
                        close_logger_on_success=False)

    # Make each corresponding taxa summary compatible so that coloring matches
    # between them. We want to be able to compare self versus other at each
    # body site.
    commands = []
    valid_body_sites = []
    for body_site_cat_value in body_site_cat_values:
        personal_cat_vals = list(personal_cat_values)

        ts_dir = join(output_dir, '%s_%s_%s' % (
                ts_dir_prefix, personal_cat_vals[0], body_site_cat_value))

        if not exists(ts_dir):
            continue

        # Check that we have 2+ weeks (samples were previously collapsed into
        # weeks for self and other). If we don't have 2+ weeks,
        # plot_taxa_summary.py will fail, so we'll skip this body site.
        weeks_otu_table_fp = join(ts_dir,
                                  '%s_otu_table_sorted.biom' % time_series_cat)
        with open(weeks_otu_table_fp, 'U') as weeks_otu_table_f:
            if _count_num_samples(weeks_otu_table_f) < 2:
                continue

        ts_fps1 = sorted(glob(join(ts_dir,
                '%s_otu_table_sorted_L*.txt' % time_series_cat)))

        ts_dir = join(output_dir, '%s_%s_%s' % (
                ts_dir_prefix, personal_cat_vals[1], body_site_cat_value))

        if not exists(ts_dir):
            continue

        weeks_otu_table_fp = join(ts_dir,
                                  '%s_otu_table_sorted.biom' % time_series_cat)

        with open(weeks_otu_table_fp, 'U') as weeks_otu_table_f:
            if _count_num_samples(weeks_otu_table_f) < 2:
                continue

        ts_fps2 = sorted(glob(join(ts_dir,
                '%s_otu_table_sorted_L*.txt' % time_series_cat)))

        if len(ts_fps1) != len(ts_fps2):
            raise ValueError("There are not an equal number of taxa summaries "
                             "to compare between self and other.")

        compatible_ts_dir = join(output_dir,
                                 'compatible_ts_%s' % body_site_cat_value)
        dirs_to_remove.append(compatible_ts_dir)

        compatible_ts_fps = defaultdict(list)
        for ts_fp1, ts_fp2 in zip(ts_fps1, ts_fps2):
            if basename(ts_fp1) != basename(ts_fp2):
                raise ValueError("Could not find matching taxa summaries "
                                 "between self and other to compare.")

            # Make taxa summaries compatible.
            cmd_title = 'Making compatible taxa summaries (%s)' % personal_id
            cmd = ('compare_taxa_summaries.py -i %s,%s -o %s -m paired -n 0' %
                   (ts_fp1, ts_fp2, compatible_ts_dir))
            commands.append([(cmd_title, cmd)])

            compatible_ts_fps[personal_cat_vals[0]].append(
                    join(compatible_ts_dir, add_filename_suffix(ts_fp1,
                        '_sorted_and_filled_0')))

            compatible_ts_fps[personal_cat_vals[1]].append(
                    join(compatible_ts_dir, add_filename_suffix(ts_fp2,
                         '_sorted_and_filled_1')))

        for personal_cat_value in personal_cat_values:
            # Plot taxa summaries.
            ts_fps = ','.join(sorted(compatible_ts_fps[personal_cat_value]))

            ts_plots_dir = join(output_dir, 'taxa_plots_%s_%s' % (
                    personal_cat_value, body_site_cat_value),
                    'taxa_summary_plots')

            cmd_title = 'Plot taxa summaries (%s)' % personal_id
            cmd = ('plot_taxa_summary.py -i %s -o %s -a numeric' %
                   (ts_fps, ts_plots_dir))
            commands.append([(cmd_title, cmd)])

        # If we've gotten this far, we'll be able to process this body site
        # (i.e. there are enough weeks).
        valid_body_sites.append(body_site_cat_value)

    # Hack to allow print-only mode.
    if command_handler is not print_commands and not valid_body_sites:
        raise ValueError("None of the body sites for personal ID '%s' could "
                         "be processed because there were not enough weeks "
                         "to create taxa summary plots." % personal_id)

    command_handler(commands, status_update_callback, logger,
                    close_logger_on_success=False)

    return files_to_remove, dirs_to_remove

def _count_num_samples(otu_table_f):
    """Returns the number of samples in the OTU table."""
    return len(parse_biom_table(otu_table_f).SampleIds)

def _count_per_individual_samples(otu_table_f, map_f, pid_col, pid):
    """Returns the number of samples in the OTU table for the individual."""
    otu_table = parse_biom_table(otu_table_f)
    mapping_data, header, comments = parse_mapping_file(map_f)
    sid_idx = header.index('SampleID')
    pid_idx = header.index(pid_col)

    sids = []
    for row in mapping_data:
        if row[pid_idx] == pid:
            sids.append(row[sid_idx])

    return len(set(sids) & set(otu_table.SampleIds))

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
    email_password = email_settings['password']
    server = email_settings['smtp_server']
    port = email_settings['smtp_port']

    if dry_run:
        num_recipients = len(recipients)

        print("Running script in dry-run mode. No emails will be sent. Here's "
              "what I would have done:\n")
        print("Sender information:\n\nFrom address: %s\nPassword: %s\nSMTP "
              "server: %s\nPort: %s\n" % (sender, email_password, server,
                                          port))
        print "Sending emails to %d recipient(s)." % num_recipients

        if num_recipients > 0:
            # Sort so that we will grab the same recipient each time this is
            # run over the same input files.
            sample_recipient = sorted(recipients.items())[0]
            personal_id = sample_recipient[0]
            password, addresses = sample_recipient[1]

            print "\nSample email:\n"
            print "To: %s" % ', '.join(addresses)
            print "From: %s" % sender
            print "Subject: %s" % notification_email_subject
            print "Body:\n%s\n" % get_personalized_notification_email_text(
                    personal_id, password)
    else:
        for personal_id, (password, addresses) in recipients.items():
            personalized_text = \
                    get_personalized_notification_email_text(personal_id,
                                                             password)
            print "Sending email to %s (%s)... " % (personal_id,
                                                    ', '.join(addresses)),
            send_email(server, port, sender, email_password, addresses,
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

def generate_passwords(pids_f, results_dir, password_dir, out_dir):
    """Creates PID -> password mapping, .htaccess files, and .htpasswd file."""
    htpasswd_f = open(join(out_dir, '.htpasswd'), 'w')
    pid_passwd_f = open(join(out_dir, 'personal_ids_with_passwords.txt'), 'w')

    for line in pids_f:
        pid = line.strip()
        pid_dir = join(results_dir, pid)

        if not exists(pid_dir):
            raise ValueError("The '%s' directory does not exist. Cannot "
                             "create a password for an individual without "
                             "results." % pid_dir)

        htaccess_f = open(join(pid_dir, '.htaccess'), 'w')
        htaccess_f.write(format_htaccess_file(password_dir, pid))
        htaccess_f.close()

        password, encrypted_password = generate_random_password()
        htpasswd_f.write('%s:%s\n' % (pid, encrypted_password))
        pid_passwd_f.write('%s\t%s\n' % (pid, password))

    htpasswd_f.close()
    pid_passwd_f.close()

def generate_random_password(min_len=8, max_len=12):
    """Returns a random alphanumeric password of random length.

    Returns both unencrypted and encrypted password. Encryption is performed
    via Apache's htpasswd command, using their custom MD5 algorithm.

    Length will be randomly chosen from within the specified bounds
    (inclusive).
    """
    # Modified from
    # http://code.activestate.com/recipes/59873-random-password-generation
    chars = letters + digits
    length = randint(min_len, max_len)
    password = ''.join([choice(chars) for i in range(length)])

    # This is hackish but should work for now...
    stdout, stderr, ret_val = qiime_system_call('htpasswd -nbm foobarbaz %s' %
                                                password)
    if ret_val != 0:
        raise ValueError("Error executing htpasswd command. Do you have this "
                         "command on your machine?")

    # Will be in the form foobarbaz:<encrypted password>
    encrypted_password = stdout.strip().split('foobarbaz:', 1)[1]

    return password, encrypted_password
