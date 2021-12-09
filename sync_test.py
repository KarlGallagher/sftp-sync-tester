# Copyright (c) 2021 Karl Gallagher
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import sys
import os
import logging
import argparse
import time
import multiprocessing
import pysftp

from config import Configuration

# Global Logger
logger:logging.Logger = None


def parse_input_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i",
        "--input_file_path",
        dest="input_file_path",
        default=None,
        required=True,
        help="Path to input file, including filename - (required)")

    parser.add_argument(
        "-u",
        "--upload_file_path",
        dest="upload_file_path",
        default=None,
        required=True,
        help="remote path for upload, including filename - (required)")
    
    parser.add_argument(
        "-o",
        "--output_file_path",
        dest="output_file_path",
        default=None,
        required=True,
        help="local path for download, including filename - (required)")

   
    try:
        parsed_args = parser.parse_args()

        # handle zero args
        if len(sys.argv) == 1:
            parser.print_help()
            sys.exit(0)
        validate_input_args(parsed_args)
        return parsed_args

    except argparse.ArgumentError:
        print("caught ArgumentError")
        parser.print_help()
        sys.exit(0)

    except Exception:
        print("caught Exception")
        parser.print_help()
        sys.exit(0)

# =================================================================================================


def validate_input_args(args: argparse.Namespace) -> None:
    if args.input_file_path is None:
        log_and_exit("Input File is a mandatory argument, see help options")

    if os.path.isfile(args.input_file_path) is not True:
        log_and_exit("[{}] Input File not found".format(args.input_file_path))

    if args.upload_file_path is None:
        log_and_exit("Upload File Path is a mandatory argument, see help options")
    
    if args.output_file_path is None:
        log_and_exit("Output File is a mandatory argument, see help options")

# =================================================================================================


def log_and_exit(msg: str) -> None:
    logger.error(msg)
    sys.exit(1)

# =================================================================================================


def setup_logging(name: str) -> logging.Logger:
    global logger
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(name)
    return logger

# =================================================================================================


def upload_file(cfg: Configuration, log: logging.Logger, path: str, file: str) -> int:

    print("Starting SFTP transfer of file - {} to Server - {}:{} /{}".format(file, cfg.SFTP_HOST, cfg.SFTP_PORT, path))

    try:
        opts = pysftp.CnOpts()
        opts.hostkeys = None  
        with pysftp.Connection(host=cfg.SFTP_HOST, port=cfg.SFTP_PORT, username=cfg.SFTP_USERNAME, password=cfg.SFTP_PASSWORD) as sftp:            
            sftp.put(localpath=file, remotepath=path)
            print("SFTP file upload complete")
    except:
        log.error("SFTP file upload failed")
        e_type, e_value, e_backtrace = sys.exc_info()
        log.error("Error: \n {} \n".format(str(e_type), str(e_backtrace)), exc_info=1, stack_info=True)
        return -1

    return 0

# =================================================================================================


def download_file(cfg: Configuration, log: logging.Logger, file: str, path: str) -> int:
    # delay this task based on user config timeout
    time.sleep(cfg.SLEEP_TIMEOUT_MS / 1000.0)
    try:
        opts = pysftp.CnOpts()
        opts.hostkeys = None  
        with pysftp.Connection(host=cfg.SFTP_HOST, port=cfg.SFTP_PORT, username=cfg.SFTP_USERNAME, password=cfg.SFTP_PASSWORD) as sftp:
            with sftp.cd(file.split('/')[0] +'/'):             
                files = sftp.listdir()
                print("Directory listing...")
                print('\n'.join(files))
                print("...")
            print("Starting SFTP transfer of file - {} from Server - {}:{} ->{}".format(file, cfg.SFTP_HOST, cfg.SFTP_PORT, path))
            sftp.get(remotepath=file, localpath=path)
            print("SFTP file download complete")
    except:
        log.error("SFTP file download failed")
        e_type, e_value, e_backtrace = sys.exc_info()
        log.error("Error: \n {} \n".format(str(e_type), str(e_backtrace)), exc_info=1, stack_info=True)
        return -1

    return 0

# =================================================================================================


def transfer_files_and_wait(args: argparse.Namespace, log: logging.Logger) -> None:
    pool = multiprocessing.Pool(processes=2)
    results = []
    return_code = -1

    results.append(pool.apply_async(upload_file, (Configuration, log, args.upload_file_path, args.input_file_path)))
    results.append(pool.apply_async(download_file, (Configuration, log, args.upload_file_path, args.output_file_path)))

    #execute tasks concurrently and wait for completion
    pool.close()
    pool.join()

    for result in results:
        return_code = result.get()
        if return_code != 0:
            raise RuntimeError('A file transfer has failed')

# =================================================================================================


def main(log: logging.Logger) -> None:
    log.info("SFTP File Transfer Sync Tester")
    transfer_files_and_wait(parse_input_arguments(), log)

# =================================================================================================


if __name__ == '__main__':
    try:
        main(setup_logging("sync_test.py"))
    except RuntimeError as err:
        log_and_exit("RuntimeError \n {}".format(str(err)))
    except KeyError as err:
        log_and_exit("KeyError \n {}".format(str(err)))
    except Exception as err:
        log_and_exit("Unknown Exception caught \n {}".format(str(err)))