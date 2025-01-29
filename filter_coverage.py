#!/usr/bin/env python3
#
# Robert Jakob 2025
#
# File that is able to filter coverage information
# Current focus:
#   Filtering branches that are not related to ifs, switches and whiles
#
# Features:
# - filter by file (regex)
# - filter by function name (demangled!)
# - filter by function name in file
# - filter branches that are hidden in code (e.g. throws, ...) non-ifs, non-whiles, non-switch
#
# Command line:
# filter_info f1 -o filtered_f2 --filter-non-visible-branches --filter-function main --filter-file

# Documentation from `man geninfo`
##  TN:<test name>
##
##       For each source file referenced in the .da file, there is a section containing filename and coverage data:
##
##         SF:<absolute path to the source file>
##
##       Following is a list of line numbers for each function name found in the source file:
##
##         FN:<line number of function start>,<function name>
##
##       Next, there is a list of execution counts for each instrumented function:
##
##         FNDA:<execution count>,<function name>
##
##       This list is followed by two lines containing the number of functions found and hit:
##
##         FNF:<number of functions found>
##         FNH:<number of function hit>
##
##       Branch coverage information is stored which one line per branch:
##
##         BRDA:<line number>,<block number>,<branch number>,<taken>
##
##       Block number and branch number are gcc internal IDs for the branch. Taken is either '-' if the basic block containing the branch was never executed or a number indicating how often that branch was taken.
##
##       Branch coverage summaries are stored in two lines:
##
##         BRF:<number of branches found>
##         BRH:<number of branches hit>
##
##       Then there is a list of execution counts for each instrumented line (i.e. a line which resulted in executable code):
##
##         DA:<line number>,<execution count>[,<checksum>]
##
##       Note that there may be an optional checksum present for each instrumented line. The current geninfo implementation uses an MD5 hash as checksumming algorithm.
##
##       At the end of a section, there is a summary about how many lines were found and how many were actually instrumented:
##
##         LH:<number of lines with a non-zero execution count>
##         LF:<number of instrumented lines>
##
##       Each sections ends with:
##
##         end_of_record

import subprocess
import argparse

# def demangle(names):
#     args = ['c++filt']
#     args.extend(names)
#     pipe = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
#     stdout, _ = pipe.communicate()
#     demangled = stdout.split("\n")
# 
#     # Each line ends with a newline, so the final entry of the split output
#     # will always be ''.
#     assert len(demangled) == len(names)+1
#     return demangled[:-1]

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
