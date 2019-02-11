from concurrent.futures import ThreadPoolExecutor, as_completed
from gc import collect


class ThreadWrapper(object):
    def __init__(self, threads_count, debug=False):
        self.threadsPool = None
        self._threads_count = threads_count
        self._is_debug = debug
        self._setup_threads()
        self._futures = None
        
    def _setup_threads(self):
        self.threadsPool = ThreadPoolExecutor(self._threads_count)

    def execute_method(self, method, objects):
        _results = {}
        try:
            self._futures = {self.threadsPool.submit(obj.__getattribute__(method)): idx for idx, obj in enumerate(objects)}
            _tasks = len(self._futures)
            _tenth = round(_tasks / 10)
            if self._is_debug:
                print('Formed a pool of {} tasks with {} workers'.format(_tasks, self._threads_count))
            for _idx, future in enumerate(as_completed(self._futures)):
                i = self._futures[future]
                try:
                    data = future.result()
                    _results[i] = data
                except Exception as exc:
                    self.threadsPool._threads.clear()
                    print('{} generated an exception: {}'.format(objects[i], exc))
                if self._is_debug:     
                    if _tenth != 0 and _idx != 0 and _idx % _tenth == 0:
                        print('{}% Done'.format((_idx // _tenth) * 10))
        except Exception as e:
            print(e)
        finally:
            _results = self._sort_results(_results)
            self.threadsPool.shutdown(wait=True)
            # clear heap
            collect()
            return _results

    def _sort_results(self, res):
        return [v for _, v in sorted(res.items())]