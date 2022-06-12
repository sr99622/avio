import avio
import argparse

class Trimmer:
    def trim(self, args):

        process = avio.Process()

        start = 0
        if args.start:
            start = args.start * 1000

        end = 0
        if args.end:
            end = args.end * 1000
        
        process.trim(eval(args.filename), eval(args.output), start, end)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="trim media file")
    parser.add_argument("filename", metavar="filename", type=ascii, help="media file to trim")
    parser.add_argument("--output", type=ascii, required=True, help="output file")
    parser.add_argument("--start", type=int, help="start time in seconds")
    parser.add_argument("--end", type=int, help="end time in seconds")
    args = parser.parse_args()

    trimmer = Trimmer()
    trimmer.trim(args)
