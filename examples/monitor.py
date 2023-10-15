
import json, time, platform, argparse
import datetime as dt
from traceback import format_exc

from multiprocessing import Process, Manager




import random

NUM_RETRIES = 3


class SocketClient():
    def __init__(self, port, q):
        self.host = "127.0.0.1"
        self.port = port
        self.id = random.randrange(1,100)
        self.send_q = q

    def wait_for_message(self, socket):
        received = False
        attempts = 10
        message = False
        while not received and (attempts > 0):
            time.sleep(0.1)
            try:
                message = socket.recv()
                received = True
            except Exception as e:
                attempts -= 1
        return message
    
    def main_task(self):
        while True:
            if len(self.send_q) == 0:
                time.sleep(0.5)
            else:
                msg = self.send_q.pop()
                if msg != "DEBUG":
                    self.connect_and_send(msg[0], msg[1])   
                    logger.info(f"Sent message: {msg}")         
            time.sleep(1)


    def connect_and_send(self, name, msg):
        done = False
        attempts = 0
        logger.info(f"Starting command process for {name}.")
        with connect(f"ws://{self.host}:{self.port}") as websocket:
            

            def retry(error_type, attempts, error="Unknown"):
                logger.warning(f"Encountered {error_type} error for {name}: {error}, retrying...")
                attempts += 1
                time.sleep(1)
                websocket.send(msg)
                return attempts
            
            while attempts == 0:
                try:
                    websocket.send(msg)
                    attempts = 1
                except Exception as e:
                    logger.warning(f"Failed to send command for {name}, re-attempting")
                    time.sleep(.2)
            
            while not done:
                time.sleep(0.1)
                try:
                    message = self.wait_for_message(websocket)
                    if "SUCCESS" in message:
                        logger.success(f"Command for {name} executed with success on attempt {attempts}")
                        done = True
                    if message == "ERROR":
                        if attempts == NUM_RETRIES:
                            logger.error(f"Failed to execute {name} command")
                            done = True
                        else:
                            attempts = retry("backend", attempts)
                except Exception as e:
                    attempts = retry("socket", attempts, error=e)
            time.sleep(0.1)
            # logger.info(f"closing connection for {self.name}")
                

    def send_file_import_cmd(self, source, filename, q):
        data = dict({'cmd' : 'FILE', 'name' : source, 'file'  : filename})
        if '.swp' not in filename:
            msg = json.dumps(data)
            time.sleep(2)
            logger.info(f"Adding File command for {source} to message queue")
            q.append([source, msg])
            logger.info(f"Current Queue:")
            logger.info(q)
            # self.connect_and_send(source, msg)

   
class Handler(watchdog.events.PatternMatchingEventHandler):
    def __init__(self, client, subdirs, q):
        # Set the patterns for PatternMatchingEventHandler
        watchdog.events.PatternMatchingEventHandler.__init__(self, ignore_directories=True, case_sensitive=False)
        self.client : SourceManager = client
        self.subdirs = subdirs
        self.prev_file = ""
        self.last_send = dt.datetime.now()
        self.q = q

    def send_file_command(self, file):
        sources = self.parse_source_from_file(file)
        for source in sources:
            if (self.prev_file != file) or ((dt.datetime.now() - self.last_send).seconds > .1):
                if source:
                    try:
                        self.client.comm.send_file_import_cmd(source, file, self.q)
                    except Exception as e:
                        logger.error(f"Failed to send import command for {source}")
                        print(format_exc())
            time.sleep(0.5)
        self.prev_file = file
        self.last_send = dt.datetime.now()

    def parse_source_from_file(self, file):
        sources = []
        
        for flag, source in self.subdirs.items():
            #print(f"{flag}, {file}")
            if flag in file:
                #print("match")
                sources.append(source)
        return sources

    def on_created(self, event):
        pass
        # print(f"CREATED: {event.src_path}")
        # if ".swp" not in event.src_path:
        #     time.sleep(1)
        #     self.send_file_command(event.src_path)

    def on_modified(self, event):
        if ".swp" not in event.src_path:
            # time.sleep(1)
            self.send_file_command(event.src_path)
        

class SourceManager():
    def __init__(self, name, dir, subdirs, port, comm, q):
        self.name = name
        self.host = "127.0.0.1"
        self.port = port
        self.comm : SocketClient = comm # SocketClient(self.name, port)
        self.dir = dir
        
        self.handler = Handler(self, subdirs, q)
        self.observer = watchdog.observers.Observer()

    def begin_watch(self):
        self.observer.schedule(self.handler, self.dir, recursive = True)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
                t = dt.datetime.now()
                if (t.hour == 0) and (t.minute == 0) and (t.second >= 50):
                    raise SystemExit
        except KeyboardInterrupt:
            self.observer.stop()
        except Exception:
            print(format_exc())

            
            
    

def main(port):
    logger.info(f"Starting Monitor, sending commands on port {port}")
    m = Manager()
    MESSAGE_Q = m.list([])
    comm = SocketClient(port, MESSAGE_Q)
    monitors : list[SourceManager] = []
    proc = []
    for g in source_groups:
        name = g['name']
        dir = g['dir']
        subdirs = g['subdirs']
        mon = SourceManager(name, dir, subdirs, port, comm, MESSAGE_Q)
        monitors.append(mon)
    try:
        
        p = Process(target=comm.main_task)
        p.start()
        proc.append(p)
        for mon in monitors:
            p = Process(target=mon.begin_watch)
            p.start()
            proc.append(p)
        for p in proc:
            p.join()

    except SystemExit as e:
        for p in proc:
            p.terminate()
    except Exception as eg:
        print(format_exc())
        raise
    


if __name__ == "__main__":
    logger.add("../outputs/server.log", level="DEBUG", colorize=False)
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', action='store_true')
    args = parser.parse_args()
    port = 1885
    if args.d:
        port = 1887
    
    main(port)