import avio
import argparse

class Merger:
    def merge(self, args):
        inputs = []
        for file in args.filenames:
            print(eval(file))
            inputs.append(eval(file))

        process = avio.Process()
        process.merge_filenames = inputs
        process.merge(eval(args.output))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="merge like files")
    parser.add_argument("filenames", metavar="filenames", type=ascii, nargs="+", help="input files to merge")
    parser.add_argument("--output", type=ascii, required=True, help="output file")
    args = parser.parse_args()

    merger = Merger()
    merger.merge(args)