#!/usr/bin/env python3

import subprocess
import argparse

def get_line_from_source(filename, line):
    src = open(filename, "r")
    return src.readlines()[line-1]

def source_contains_syntactic_branch(test,file_name,function,line,block,branch,taken_count):
    source_line = get_line_from_source(file_name, int(line))
    if (source_line.strip().startswith('if')
            or source_line.strip().startswith('while')
            or source_line.strip().startswith('case')
            or source_line.strip().startswith('} while')
            or source_line.strip().startswith('switch')
            ):
        return True

    return False

class CoverageFilter:
    # The options to use are:
    #   "ignore-hidden-branches" -> filters out branches that do not have a syntax correspondance in the code (e.g. no if, while, ...)
    def __init__(self, lines, **options):
        self.lines = lines
        self.ignore_hidden_branches = options.get('ignore_hidden_branches', False)
        filereg = options.get('ignore_file_regex', [])
        self.ignore_file_regex = filereg if isinstance(filereg, list) else [filereg]
        # print("Option {}".format(self.ignore_hidden_branches))

    def doPrint(*pos):
        # print(*pos)
        pass

    def filter(self):
        output = []
        function_active = False

        # State
        active_test = ""
        active_file = ""
        active_function = ""

        ignore_function = False
        ignore_file = False

        for line in self.lines:
            if line.startswith("TA:"):
                active_test = line[3:-1]
                self.doPrint("Active test: " + active_test)

            if line.startswith('SF:'):
                active_file = line[3:-1]
                self.doPrint("Active source file: " + active_file)

            if line.startswith('FN:'):
                active_function = line[3:-1].split(',')[1]
                self.doPrint("Active function: " + active_function)

            if line.startswith('DA:'):
                if (ignore_function or ignore_file):
                    continue

            if line.startswith('BRDA:'):
                if (ignore_function or ignore_file):
                    continue

                if self.ignore_hidden_branches:
                    parts = line[5:-1].split(',')
                    line_number = parts[0]
                    block_number = parts[1]
                    branch_number = parts[2]
                    taken_count = parts[3]

                    if not source_contains_syntactic_branch(active_test,active_file,active_function,line_number,block_number,branch_number,taken_count):
                        self.doPrint("Ignoring: " + active_test + " " + active_file + " " + active_function + " " + line_number)
                        continue

            if line.startswith('end_of_record'):
                active_function = ""
                
            output.append(line)
        return output

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='filter_coverage',
                    description='Filters a coverage info file as created by lcov.',
                    epilog='')
    parser.add_argument('info_file_name')
    parser.add_argument('--filter_non_visible_branches', action='store_true')

    args = parser.parse_args()
    
    cov_file = open(args.info_file_name, "r")
    lines = cov_file.readlines()

    cf = CoverageFilter(lines, ignore_hidden_branches=args.filter_non_visible_branches)
    output = cf.filter()

    print(''.join(output),end='')
