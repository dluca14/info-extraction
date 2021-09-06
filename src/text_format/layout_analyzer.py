import json
import math
import re
import pprint


def compute_average_line_height(words):
    sum_up = 0
    for word in words:
        sum_up += (word['y2'] - word['y1'])
    return math.ceil(sum_up/len(words)) if len(words) > 0 else 0


def compute_minimum_line_spacing(words):
    lines = {}
    # find all words per line
    for word in words:
        if not word['line'] in lines:
            lines[word['line']] = {'y1': word['y1'], 'y2': word['y2']}
        else:
            if word['y1'] <= lines[word['line']]['y1']:
                lines[word['line']]['y1'] = word['y1']
            if word['y2'] >= lines[word['line']]['y2']:
                lines[word['line']]['y2'] = word['y2']
    count = 0
    minimum_line_spacing = 1000000
    for key in lines:
        count += 1
        if count == 1:
            previous_key = key
            continue
        curent_line_spacing = lines[key]['y1'] - lines[previous_key]['y2']
        if curent_line_spacing < minimum_line_spacing:
            minimum_line_spacing = curent_line_spacing
        previous_key = key

    return 40 if minimum_line_spacing == 1000000 else minimum_line_spacing


def compute_average_word_spacing(words):
    lines = {}
    # find all words per line
    for word in words:
        if not word['line'] in lines:
            lines[word['line']] = []
        lines[word['line']].append(word)

    distance_sum = 0
    distance_count = 0
    # find words that are close by on the line and add their distance to the average
    for key in lines:
        words_in_line = lines[key]
        if len(words_in_line) <= 1:
            continue
        for i in range(len(words_in_line) - 1):
            distance = words_in_line[i + 1]['x1'] - words_in_line[i]['x2']
            if 0 < distance < 50:
                distance_sum += distance
                distance_count += 1

    return math.floor((distance_sum / distance_count) * 1.5) if (distance_sum > 0 and distance_count > 0) else 40


def clear_word_noise(words, average_line_height, page_width):
    result = []
    for word in words:
        word_height = word['y2'] - word['y1']
        word_width = word['x2'] - word['x1']
        if word_height > math.floor(average_line_height / 8) and word_height < average_line_height * 4 and word_width < (page_width * 0.6):
            result.append(word)
    return result


def cluster_words_into_blocks(words, average_line_height, minimum_line_spacing):
    blocks = []
    seed = find_new_seed(words)
    while seed:
        current_block = collect_block(seed, words, average_line_height, minimum_line_spacing)
        blocks.append(current_block)
        seed = find_new_seed(words)
    blocks = sorted(blocks, key=compare_by_id)
    return blocks


def find_new_seed(words):
    for word in words:
        if 'marked' not in word:
            return word


def collect_block(seed, words, average_line_height, minimum_line_spacing):
    block = {"words": []}
    block_words = []
    neighbours = find_top_bottom_neighbours(seed, words, average_line_height, minimum_line_spacing)
    for neighbour in neighbours:
        block_words.append(neighbour)

    while len(neighbours) > 0:
        neighbours_of_neighbours = []
        for neighbour in neighbours:
            new_neighbours = find_top_bottom_neighbours(neighbour, words, average_line_height, minimum_line_spacing)
            if len(new_neighbours) > 0:
                for new_neighbour in new_neighbours:
                    block_words.append(new_neighbour)
                    neighbours_of_neighbours.append(new_neighbour)
        neighbours = neighbours_of_neighbours

    return create_block(block_words)


def create_block(words):
    block = {'words': words}
    block['words'] = sorted(block['words'], key=compare_by_id)
    block['id'] = block['words'][0]['id']
    block['count'] = len(block['words'])
    block['t'] = ""
    block['x1'] = block['words'][0]['x1']
    block['y1'] = block['words'][0]['y1']
    block['x2'] = block['words'][0]['x2']
    block['y2'] = block['words'][0]['y2']
    block['lines'] = []
    for word in block['words']:
        block['t'] += " "
        block['t'] += word['t'][0]
        if block['x1'] > word['x1']:
            block['x1'] = word['x1']
        if block['y1'] > word['y1']:
            block['y1'] = word['y1']
        if block['x2'] < word['x2']:
            block['x2'] = word['x2']
        if block['y2'] < word['y2']:
            block['y2'] = word['y2']
        block['lines'].append(word['line'])

    block['number_ratio'] = compute_numbers_ratio(block['t'])
    # make distinct here
    block['lines'] = list(set(block['lines']))
    block['lines'] = sorted(block['lines'], key=lambda x: int(x[5:len(x)]))
    block['type'] = compute_block_type(block)
    return block


def compute_block_type(block):
    for word in block['words']:
        horizontal_neighbours = []
        for word_filtered in block['words']:
            if word_filtered['id'] != word['id'] and \
                    ((word['y1'] <= word_filtered['y1'] <= word['y2']) or
                        (word['y1'] <= word_filtered['y2'] <= word['y2'])):
                horizontal_neighbours.append(word_filtered)
        if len(horizontal_neighbours) > 0:
            return 2
    return 1


def find_top_bottom_neighbours(seed, words, average_line_height, minimum_line_spacing):
    height = average_line_height
    if minimum_line_spacing > 0:
        height = math.floor((average_line_height + minimum_line_spacing * 2) / 3) + math.floor(average_line_height / 4)

    search_box_x1 = seed['x1']
    search_box_y1 = seed['y1'] - height
    search_box_x2 = seed['x2']
    search_box_y2 = seed['y2'] + height
    result = []
    for word in words:
        if 'marked' not in word and \
                ((search_box_x1 <= word['x1'] <= search_box_x2) or (search_box_x1 <= word['x2'] <= search_box_x2) or
                 (word['x1'] <= search_box_x1 and word['x2'] >= search_box_x2)) and \
                ((search_box_y1 <= word['y1'] <= search_box_y2) or (search_box_y1 <= word['y2'] <= search_box_y2)):
            word['marked'] = True
            result.append(word)
    return result


def compare_by_id(a):
    return int(a['id'][5:len(a['id'])])


def find_horizontal_neighbourhoods(blocks):
    hn = []
    seed = find_new_seed(blocks)
    if seed:
        seed['marked'] = True
    while seed:
        current_hn = collect_horizontal_neighbours(seed, blocks)
        hn.append(current_hn)
        seed = find_new_seed(blocks)
        if seed:
            seed['marked'] = True
    return hn


def collect_horizontal_neighbours(seed, blocks):
    new_blocks = []
    neighbours = find_horizontal_neighbours(seed, blocks)
    new_blocks.append(seed)
    for neighbour in neighbours:
        new_blocks.append(neighbour)
    return create_neighbourhood(new_blocks)


def create_neighbourhood(blocks):
    neighbourhood = {"blocks": blocks}
    neighbourhood['id'] = neighbourhood['blocks'][0]['id']
    neighbourhood['count'] = len(neighbourhood['blocks'])
    neighbourhood['x1'] = neighbourhood['blocks'][0]['x1']
    neighbourhood['y1'] = neighbourhood['blocks'][0]['y1']
    neighbourhood['x2'] = neighbourhood['blocks'][0]['x2']
    neighbourhood['y2'] = neighbourhood['blocks'][0]['y2']
    neighbourhood['lines'] = []
    for block in neighbourhood['blocks']:
        if neighbourhood['x1'] > block['x1']:
            neighbourhood['x1'] = block['x1']
        if neighbourhood['y1'] > block['y1']:
            neighbourhood['y1'] = block['y1']
        if neighbourhood['x2'] < block['x2']:
            neighbourhood['x2'] = block['x2']
        if neighbourhood['y2'] < block['y2']:
            neighbourhood['y2'] = block['y2']
        neighbourhood['lines'] += block['lines']

    # make distinct here */
    neighbourhood['lines'] = list(set(neighbourhood['lines']))
    neighbourhood['lines'] = sorted(neighbourhood['lines'], key=lambda x: int(x[5:len(x)]))
    neighbourhood['blocks'] = sorted(neighbourhood['blocks'], key=compare_by_id)
    return neighbourhood


def find_horizontal_neighbours(seed, blocks):
    neighbourhood = {"x1": seed['x1'], "y1": seed['y1'], "x2": seed['x2'], "y2": seed['y2']}
    result = []

    for block in blocks:
        if 'marked' not in block and \
                ((neighbourhood['y1'] <= block['y1'] <= neighbourhood['y2']) or
                 (neighbourhood['y1'] <= block['y2'] <= neighbourhood['y2']) or
                 (block['y1'] >= neighbourhood['y1'] and block['y2'] <= neighbourhood['y2']) or
                 (block['y1'] <= neighbourhood['y1'] and block['y2'] >= neighbourhood['y2'])):
            if neighbourhood['x1'] > block['x1']:
                neighbourhood['x1'] = block['x1']
            if neighbourhood['y1'] > block['y1']:
                neighbourhood['y1'] = block['y1']
            if neighbourhood['x2'] < block['x2']:
                neighbourhood['x2'] = block['x2']
            if neighbourhood['y2'] < block['y2']:
                neighbourhood['y2'] = block['y2']
            block['marked'] = True
            result.append(block)
    return result


def recluster_neighbourhoods(neighbourhoods, average_word_spacing):
    for neighbourhood in neighbourhoods:
        neighbourhood['blocksR'] = []
        blocks = neighbourhood['blocks']
        blocks = sorted(blocks, key=lambda b: b['x1'])

        seed = find_new_seed_for_recluster(blocks)
        while seed:
            blocks_to_recluster = find_blocks_to_recluster_2(seed, blocks, average_word_spacing)
            new_block = merge_blocks(blocks_to_recluster.copy())
            neighbourhood['blocksR'].append(new_block)
            seed = find_new_seed_for_recluster(blocks)

    return neighbourhoods


def find_new_seed_for_recluster(blocks):
    for block in blocks:
        if 'reclustered' not in block:
            return block


def find_blocks_to_recluster_2(seed, blocks, average_word_spacing):
    # go from left to right and verify that at least one word from the growing seed is near a word on the adjacent block
    overlap_right = 60
    collector = {"x1": seed['x1'], "y1": seed['y1'], "x2": seed['x2'] + overlap_right,
                 "y2": seed['y2'], "words": seed['words'].copy()}
    #blocks = sorted(blocks, key=lambda b: b['x1'])
    result = []
    for block in blocks:
        if 'reclustered' not in block and exist_ajacent_word(collector, block, average_word_spacing):
            block['reclustered'] = True
            collector['words'] += block['words']
            result.append(block)
    return result


def exist_ajacent_word(collector, block, average_word_spacing):
    # iterate the words of the collector and try to match words form the block
    # try to find at least one word
    collector_words = collector['words']
    block_words = block['words']
    matches = []
    for block_word in block_words:
        block_word_x1 = block_word['x1'] - average_word_spacing
        block_word_x2 = block_word['x2'] + average_word_spacing
        proximity = []

        for collector_word in collector_words:
            if block_word['line'] == collector_word['line'] and \
                    ((block_word_x1 <= collector_word['x1'] <= block_word_x2) or (
                    block_word_x1 <= collector_word['x2'] <= block_word_x2)):
                proximity.append(collector_word)
        if len(proximity) > 0:
            matches.append(block_word)

    return len(matches) > 0


def merge_blocks(blocks):
    if len(blocks) == 1:
        return blocks[0]

    new_block = {}
    new_block['words'] = []
    new_block['lines'] = []
    new_block['id'] = blocks[0]['id']
    new_block['count'] = 0
    new_block['t'] = ""
    new_block['x1'] = blocks[0]['x1']
    new_block['y1'] = blocks[0]['y1']
    new_block['x2'] = blocks[0]['x2']
    new_block['y2'] = blocks[0]['y2']
    for block in blocks:
        new_block['t'] += " "
        new_block['t'] += block['t']
        new_block['count'] += block['count']
        if new_block['x1'] > block['x1']:
            new_block['x1'] = block['x1']
        if new_block['y1'] > block['y1']:
            new_block['y1'] = block['y1']
        if new_block['x2'] < block['x2']:
            new_block['x2'] = block['x2']
        if new_block['y2'] < block['y2']:
            new_block['y2'] = block['y2']
        new_block['words'] += block['words']
        new_block['lines'] += block['lines']
    new_block['number_ratio'] = compute_numbers_ratio(new_block['t'])
    # make distinct here
    new_block['lines'] = list(set(new_block['lines']))
    new_block['lines'] = sorted(new_block['lines'], key=lambda x: int(x[5:len(x)]))
    new_block['words'] = sorted(new_block['words'], key=compare_by_id)
    new_block['type'] = compute_block_type(new_block)
    return new_block


def compute_numbers_ratio(text):
    stripped = text.replace(' ', '')
    initial_length = len(stripped)
    numbers_length = len(re.sub("[^0-9]", "", stripped))

    return 0 if numbers_length == 0 else (numbers_length / initial_length)


def split_logical_rows(neighbourhoods):
    # find a list of different lines from the neighbourhood
    # iterate the type one blocks create a set of lines which belongs only to type 1
    # intersect these lines with all blocks
    # each block having two intersections will have to be split on those lines
    # also split into new horizontal neighbourhoods
    split_neighbourhoods = []
    for neighbourhood in neighbourhoods:
        type_1_lines = []
        for block in neighbourhood['blocksR']:
            if block['type'] == 1:
                type_1_lines += block['lines']

        type_1_lines = list(set(type_1_lines))
        neighbourhood['blocksS'] = []
        for block in neighbourhood['blocksR']:
            # intersect the block lines with type1 lines if they match more than 1 times the block has to be split
            intersection = []
            for line in type_1_lines:
                if line in block['lines']:
                    intersection.append(line)
            if len(intersection) > 1:
                new_blocks = split_blocks_by_lines(block, intersection)
                neighbourhood['blocksS'] += new_blocks
            else:
                neighbourhood['blocksS'].append(block)

        if len(type_1_lines) > 1:
            # split neighbourhoods
            for type_1_line in type_1_lines:
                new_neighbourhood_blocks = []
                for block_s in neighbourhood['blocksS']:
                    if type_1_line in block_s['lines']:
                        new_neighbourhood_blocks.append(block_s)

                new_neighbourhood = create_neighbourhood_s(new_neighbourhood_blocks)
                split_neighbourhoods.append(new_neighbourhood)
        else:
            split_neighbourhoods.append(neighbourhood)

    return split_neighbourhoods


def split_blocks_by_lines(block, lines):
    blocks = []
    split_line_ranges = []
    min_line = 100000
    max_line = 0
    for word in block['words']:
        idx = extract_index(word['line'])
        if idx < min_line:
            min_line = idx
        if idx > max_line:
            max_line = idx

    structure = {}
    if f'line_{min_line}' not in lines:
        structure[min_line] = []
    i = min_line
    while i <= max_line:
        if f'line_{i}' in lines:
            structure[i] = []
        i += 1

    curent_split = 'undefined'
    i = min_line
    while i <= max_line:
        if structure.get(i) == []:
            curent_split = i
        structure[curent_split].append(f'line_{i}')
        i += 1

    for key in structure:
        split_line_range = structure[key]
        words = []
        for word in block['words']:
            if word['line'] in split_line_range:
                words.append(word)
        new_block = create_block(words)
        blocks.append(new_block)

    return blocks

def extract_index(a):
    return int(a[5:len(a)])


def create_neighbourhood_s(blocks):
    neighbourhood = {"blocksS": blocks}
    neighbourhood['id'] = neighbourhood['blocksS'][0]['id']
    neighbourhood['count'] = len(neighbourhood['blocksS'])
    neighbourhood['x1'] = neighbourhood['blocksS'][0]['x1']
    neighbourhood['y1'] = neighbourhood['blocksS'][0]['y1']
    neighbourhood['x2'] = neighbourhood['blocksS'][0]['x2']
    neighbourhood['y2'] = neighbourhood['blocksS'][0]['y2']
    neighbourhood['lines'] = []
    for block in neighbourhood['blocksS']:
        if neighbourhood['x1'] > block['x1']:
            neighbourhood['x1'] = block['x1']
        if neighbourhood['y1'] > block['y1']:
            neighbourhood['y1'] = block['y1']
        if neighbourhood['x2'] < block['x2']:
            neighbourhood['x2'] = block['x2']
        if neighbourhood['y2'] < block['y2']:
            neighbourhood['y2'] = block['y2']
        neighbourhood['lines'] += block['lines']
    # make distinct here
    neighbourhood['lines'] = list(set(neighbourhood['lines']))
    neighbourhood['lines'] = sorted(neighbourhood['lines'], key=lambda x: int(x[5:len(x)]))
    neighbourhood['blocksS'] = sorted(neighbourhood['blocksS'], key=compare_by_id)
    return neighbourhood



def find_logical_table_rows(neighbourhoods):
    result = []
    for neighbourhood in neighbourhoods:
        no_of_number_blocks = 0
        no_of_text_blocks = 0
        matches = []
        for block in neighbourhood['blocksS']:
            if block['number_ratio'] >= 0.4:
                no_of_number_blocks += 1
            else:
                no_of_text_blocks += 1
            if block['type'] == 1:
                matches.append(block)

        # TODO validate matches length
        if len(neighbourhood['blocksS']) >= 1 and no_of_number_blocks >= 1:
        # if matches.length > 0 and len(neighbourhood['blocksS']) >= 1 and no_of_number_blocks >= 1:
            result.append(neighbourhood)
    return result


def cluster_sparse_logical_rows(logical_table_rows, average_word_spacing):
    tables = []
    # sort logical table rows based on y1
    logical_table_rows = sorted(logical_table_rows, key=lambda l: l['y1'])
    # cluster based on Y of each Logical Row separate in different lists if lines differ by more than 2 average line heights
    # cluster based on X of each Logical Row to not be more than 30% difference in width
    if len(logical_table_rows) > 0:
        collector = {"logicalTableRows": [], "x1": logical_table_rows[0]['x1'], "y1": logical_table_rows[0]['y1'], "x2": logical_table_rows[0]['x2'], "y2": logical_table_rows[0]['y2']}
        collector['logicalTableRows'].append(logical_table_rows[0].copy())
        for idx, curent_row in enumerate(logical_table_rows):
            if idx == 0:
                continue
            collector_width = collector['x2'] - collector['x1']
            current_row_width = curent_row['x2'] - curent_row['x1']
            if(curent_row['y1'] - collector['y2']) < (2 * average_word_spacing) and ((collector_width / current_row_width) if collector_width > current_row_width else (current_row_width / collector_width)) < 1.3:
                collector['logicalTableRows'].append(curent_row)
                if collector['y2'] < curent_row['y2']:
                    collector['y2'] = curent_row['y2']
                if collector['x2'] < curent_row['x2']:
                    collector['x2'] = curent_row['x2']
            else:
                tables.append(collector)
                collector = {"logicalTableRows": [curent_row], "x1": curent_row['x1'], "y1": curent_row['y1'], "x2": curent_row['x2'], "y2": curent_row['y2']}
        if len(collector['logicalTableRows']) > 0:
            tables.append(collector)
    return tables


def find_columns_from_logical_tables(tables):
    result = []
    for table in tables:
        # verify if table has more than 1 row
        if len(table['logicalTableRows']) > 1:
            table['marginSpace'] = find_columns_from_logical_rows(table['logicalTableRows'])
            table['logicalTableColumns'] = merge_overlapping_margin_points(table['marginSpace'])
            table['tableStructure'] = create_table_structure(table['logicalTableRows'], table['logicalTableColumns'])
            result.append(table)
    return result


# !!!! before this step we should cluster logical rows into groups because they might belong to multiple logical tables
# Analize margin space of these columns order then by x
def find_columns_from_logical_rows(logical_table_rows):
    margin_space = { "marginPoints": [] }
    for logical_table_row in logical_table_rows:
        for block in logical_table_row['blocksS']:
            push_into_appropriate_margin_point(margin_space, block)
    return margin_space


# find a margin structure for the block if one doesn't exist create a new one
def push_into_appropriate_margin_point(margin_space, block):
    alignment_threshold = 10
    if len(margin_space['marginPoints']) == 0:
        margin_space['marginPoints'].append({"x1": block['x1'], "y1": block['y1'], "x2": block['x2'], "y2": block['y2'], "blocks": [block]})
    else:
        # search for a margin space to fit the block based on alignment +/- threshold (less than a space char)
        margin_space_matches = []
        for margin_point in margin_space['marginPoints']:
            # // TO-DO match by centered cells
            if ((margin_point['x1'] - alignment_threshold) <= block['x1'] <= (margin_point['x1'] + alignment_threshold)) or (
                    (margin_point['x2'] - alignment_threshold) <= block['x2'] <= (margin_point['x2'] + alignment_threshold)):
                margin_space_matches.append(margin_point)
        if len(margin_space_matches) == 0:
            # create new margin point
            margin_space['marginPoints'].append({"x1": block['x1'], "y1": block['y1'], "x2": block['x2'], "y2": block['y2'], "blocks": [block]})
        elif len(margin_space_matches) == 1:
            # include block in margin point
            margin_space_match = margin_space_matches[0]
            if margin_space_match['x1'] > block['x1']:
                margin_space_match['x1'] = block['x1']
            if margin_space_match['y1'] > block['y1']:
                margin_space_match['y1'] = block['y1']
            if margin_space_match['x2'] < block['x2']:
                margin_space_match['x2'] = block['x2']
            if margin_space_match['y2'] < block['y2']:
                margin_space_match['y2'] = block['y2']
            margin_space_match['blocks'].append(block)
        else:
            # multiple matches of margin points (choose one) (!!!!is this a possibility)
            # one solution might be to the two margin points
            # for now create a new margin point
            margin_space['marginPoints'].append({"x1": block['x1'], "y1": block['y1'], "x2": block['x2'], "y2": block['y2'], "blocks": ([block])})


def merge_overlapping_margin_points(margin_space):
    margin_space['marginPointsR'] = []
    margin_points = margin_space['marginPoints']
    seed = find_new_seed_for_merge(margin_points)
    while seed:
        margin_points_to_merge = find_margin_points_to_merge(seed, margin_points)
        new_margin_point = merge_margin_points(margin_points_to_merge)
        margin_space['marginPointsR'].append(new_margin_point)
        seed = find_new_seed_for_merge(margin_points)

    return margin_space


def find_margin_points_to_merge(seed, margin_points):
    result = []
    for margin_point in margin_points:
        if 'merged' not in margin_point and \
         ((seed['x1'] <= margin_point['x1'] <= seed['x2']) or
          (seed['x1'] <= margin_point['x2'] <= seed['x2']) or
          (margin_point['x1'] >= seed['x1'] and margin_point['x2'] <= seed['x2']) or
          (margin_point['x1'] <= seed['x1'] and margin_point['x2'] >= seed['x2'])):
            margin_point['merged'] = True
            result.append(margin_point)

    return result


def find_new_seed_for_merge(margin_points):
    for margin_point in margin_points:
        if 'merged' not in margin_point:
            return margin_point


def merge_margin_points(margin_points):
    new_margin_point = {"x1": margin_points[0]['x1'], "y1": margin_points[0]['y1'], "x2": margin_points[0]['x2'], "y2": margin_points[0]['y2'], "blocks": []}
    for margin_point in margin_points:
        if new_margin_point['x1'] < margin_point['x1']:
            new_margin_point['x1'] = margin_point['x1']
        if new_margin_point['y1'] < margin_point['y1']:
            new_margin_point['y1'] = margin_point['y1']
        if new_margin_point['x2'] > margin_point['x2']:
            new_margin_point['x2'] = margin_point['x2']
        if new_margin_point['y2'] > margin_point['y2']:
            new_margin_point['y2'] = margin_point['y2']
        new_margin_point['blocks'] += margin_point['blocks']
    return new_margin_point


# let's create a table structure from the logical rows and logical columns
def create_table_structure(logical_rable_rows, logical_table_columns):
    rows_nr_ratio = None
    rows_nr = None

    table = {"rows": []}
    for logical_table_row in logical_rable_rows:
        row = {"columns": [], "id": logical_table_row['id'], "lines": logical_table_row['lines']}
        for logical_table_column in logical_table_columns['marginPointsR']:
            column = {"blocks": [], "x1": logical_table_column['x1'], "y1": logical_table_row['y1'], "x2": logical_table_column['x2'], "y2": logical_table_row['y2'], "numerical": False}
            for block in logical_table_row['blocksS']:
                if (column['x1'] <= block['x1'] <= column['x2']) or (column['x1'] <= block['x2'] <= column['x2']) or \
                        (block['x1'] >= column['x1'] and block['x2'] <= column['x2']) or \
                        (block['x1'] <= column['x1'] and block['x2'] >= column['x2']):
                    column['blocks'].append(block)

            row['columns'].append(column)

        #   Find out numerical columns
        #   For each row, interate columns and make the sum of the number ratios for each column.
        #   rowsNrRadio - the array which is keeping the sum of the number ratios
        #   rowsNr - the array which is keeping the number of rows for each column in order to calculate the average ratio
        #           for each column
        # i = 0
        # for column in row['columns']:
        #     if rows_nr_ratio is None:
        #         rows_nr_ratio = [None] * len(row['columns'])
        #         rows_nr = [None] * len(row['columns'])
        #
        #     if len(column['blocks']) > 0:
        #         if rows_nr_ratio[i] is None:
        #             rows_nr_ratio[i] = column['blocks'][0]['numberRatio']
        #             rows_nr[i] = 1
        #         else:
        #             rows_nr_ratio[i] += column['blocks'][0]['numberRatio']
        #             rows_nr[i] += 1
        #     i += 1

        table['rows'].append(row)

    return table


def produce_layout(tables, segmentation, average_line_height, average_word_spacing):
    layout = []
    for paragraph in segmentation['paragraphs']:
        paragraph_contained_by_table = []
        for table in tables['tables']:
            if (table['x1'] - average_word_spacing) <= paragraph['x1'] and \
                    (table['x2'] + average_word_spacing) >= paragraph['x2'] and \
                    (table['y1'] - average_line_height) <= paragraph['y1'] and \
                    (table['y2'] + average_line_height) >= paragraph['y2']:
                paragraph_contained_by_table.append('t')

        if len(paragraph_contained_by_table) == 0:
            paragraph['type'] = 'paragraph'
            layout.append(paragraph)

    for table in tables['tables']:
        table['type'] = 'table'
        layout.append(table)

    layout = sorted(layout, key=lambda b: b['y1'])

    return layout


def result_segmentation_view(neighbourhoods):
    resulting_view = {'paragraphs': []}
    for neighbourhood in neighbourhoods:
        neighbourhood_words = []
        paragraph = {
            'x1': neighbourhood['x1'],
            'y1': neighbourhood['y1'],
            'x2': neighbourhood['x2'],
            'y2': neighbourhood['y2'],
            'lines': neighbourhood['lines']
        }
        for block in neighbourhood['blocksR']:
            neighbourhood_words += block['words']

        neighbourhood_words = sorted(neighbourhood_words, key=compare_by_id)

        text = ''
        for idx, word in enumerate(neighbourhood_words):
            #text += word['t'][0]
            text += word["t"]
            text += '' if idx == len(neighbourhood_words) - 1 else ' '

        paragraph['text'] = text
        paragraph['words'] = neighbourhood_words
        resulting_view['paragraphs'].append(paragraph)
    return resulting_view


def result_table_recognition_view(table_structures):
    resulting_view = {'tables': []}
    for table_structure in table_structures:
        table = {
          'x1': table_structure['x1'],
          'y1': table_structure['y1'],
          'x2': table_structure['x2'],
          'y2': table_structure['y2'],
          'rowsNo': len(table_structure['tableStructure']['rows']),
          'columnsNo': 0,
          'rows': []
        }
        temp_cols_no = []
        for row in table_structure['tableStructure']['rows']:
            temp_cols_no.append(len(row['columns']))
            new_row = {'cells': []}
            for column in row['columns']:
                cell = {
                    'x1': column['x1'],
                    'y1': column['y1'],
                    'x2': column['x2'],
                    'y2': column['y2'],
                    'words': [],
                    'text': ""
                }
                for block in column['blocks']:
                    cell['words'] += block['words']

                cell['words'] = sorted(cell['words'], key=compare_by_id)
                cell['text'] = ''
                for idx, word in enumerate(cell['words']):
                    cell['text'] += word['t'][0]
                    cell['text'] += '' if idx == len(cell['words']) - 1 else ' '
                new_row['cells'].append(cell)
            table['rows'].append(new_row)
        table['columnsNo'] = highest_occurence(temp_cols_no)

        resulting_view['tables'].append(table)

    return resulting_view


def highest_occurence(array):
    if len(array) == 0:
        return None
    mode_map = {}
    max_el = array[0]
    max_count = 1
    for el in array:
        if el not in mode_map:
            mode_map[el] = 1
        else:
            mode_map[el] += 1
        if mode_map[el] > max_count:
            max_el = el
            max_count = mode_map[el]
    return max_el


def layout(words_json, debug_mode=False):

    words = words_json['words']

    average_line_height = compute_average_line_height(words)
    minimum_line_spacing = compute_minimum_line_spacing(words)
    average_word_spacing = compute_average_word_spacing(words)
    page_height = words_json['height']
    page_width = words_json['width']

    words = clear_word_noise(words, average_line_height, page_width)



    result = {}

    result['words'] = words
    result['blocks'] = cluster_words_into_blocks(words, average_line_height, minimum_line_spacing)

    result['horizontal_neighbourhoods'] = find_horizontal_neighbourhoods(result['blocks'])
    result['reclustered_neighbourhoods'] = recluster_neighbourhoods(result['horizontal_neighbourhoods'], average_word_spacing)

    result['cleaned_noise_neighbourhoods'] = result['reclustered_neighbourhoods'] # clearNeighbourhoodNoiseR(result.reclusteredNeighbourhoods)

    result['logical_rows_neighbourhoods'] = split_logical_rows(result['cleaned_noise_neighbourhoods'])

    result['logical_table_rows'] = find_logical_table_rows(result['logical_rows_neighbourhoods'])
    result['tables'] = cluster_sparse_logical_rows(result['logical_table_rows'], average_word_spacing)
    result['table_structures'] = find_columns_from_logical_tables(result['tables'])
    segmentation = result_segmentation_view(result['cleaned_noise_neighbourhoods'])
    tables = result_table_recognition_view(result['table_structures'])
    layout = produce_layout(tables, segmentation, average_line_height, average_word_spacing)
    if debug_mode is True:
        result['layout'] = layout
        return result

    return {"layout": layout}