import asyncio
import ctypes
import logging


class BackTrackingTreeMetaclass(object):
    """
        run c plus program
        translate
    """

    class SentenceHandlerFactory:
        """
        in this factory, we will translate every sentence into a coding tree
        the function and operation will be provided by so or dll file
        now the operation available are as blow:
            int get_new_tree(); return new tree with its id;create a new empty node;


            void tree_node.set_left_child
            void tree_node.set_right_child
            void tree_node.set_brother

            void stack.pull_and_set;
            void stack.push;

        """

        def __init__(self, present_sentence_list, sentence_index, status):
            # when object is created, it will scan the _do_* method below, then translate them to line
            self.sentence = present_sentence_list[sentence_index]
            self.sentence_index = sentence_index
            self.present_sentence_list = present_sentence_list
            self.result = ""
            self.status = status
            for element in dir(self):
                if element.startswith("_do"):
                    fn = getattr(self, element)
                    fn()
            self._translate()

        def _do_check_at_first_sentence(self):
            if self.sentence.startswith("THEN"):
                self.result = self.sentence[5:]
                self.status["connection"].append((self.sentence_index - 1, self.sentence_index))
            elif self.sentence == "END":
                self.result = lambda order: 1
                self.status["connection"].append((self.sentence_index - 1, self.sentence_index))
            else:
                self.result = self.sentence
                self.status["connection"].append((self.sentence_index - 1, self.sentence_index))

        def _do_check_if_sentence(self):
            if "condition" not in self.status.keys():
                self.status["condition"] = []
                self.status["stack"]["condition"] = 0
            logging.debug("handle %s when condition is %s" % (self.result, self.status["condition"]))
            if self.sentence.startswith("IF"):
                self.status["stack"]["condition"] += 1
                self.status["condition"] += [[self.sentence_index]]
                self.result = self.sentence[3:]
                logging.debug(
                    "the sentence %s ,whose index is %s, detected to be if sentence" %
                    (self.result, self.sentence_index))

            elif self.sentence.startswith("ELSE IF"):
                if not self.status["condition"]:
                    # that is to say, no if sentence before
                    raise Exception

                self.status['connection'].append((self.status["condition"][-1][-1], self.sentence_index))
                self.status["condition"][-1].append(self.sentence_index)
                self.status["toward_only"].append(self.sentence_index)
                self.result = self.sentence[8:]
                logging.debug(
                    "the sentence %s ,whose index is %s, detected to be else if sentence" %
                    (self.result, self.sentence_index))
                logging.debug(
                    "due to else if sentence, "
                    "the connection between %s and %s should be made when handling %s whose index is %s"
                    % (self.status["condition"][-1][-1], self.sentence_index, self.result, self.sentence_index))

            elif self.sentence.startswith("ELSE"):
                self.status['connection'].append((self.status["condition"][-1][-1], self.sentence_index))
                self.status["toward_only"].append(self.sentence_index)
                self.status["condition"][-1].append(self.sentence_index)
                self.result = self.sentence[5:]
                logging.debug(
                    "the sentence %s ,whose index is %s, detected to be else sentence" %
                    (self.result, self.sentence_index))
                logging.debug(
                    "due to else sentence, "
                    "the connection between %s and %s should be made when handling %s whose index is %s"
                    % (self.status["condition"][-1][-2], self.sentence_index, self.result, self.sentence_index))

            elif self.sentence.startswith("ENDIF"):
                self.status["stack"]["condition"] -= 1
                self.status["connection"].append((self.status["condition"][-1][-1], self.sentence_index))
                logging.debug(
                    "due to else sentence, "
                    "the connection between %s and %s should be made when handling endif whose index is %s"
                    % (self.status["condition"][-1][-1], self.sentence_index, self.sentence_index))
                for i in range(len(self.status['condition'][-1]) - 1):
                    # connect endif and the last sentence of previous condition sentence
                    self.status["connection"].append((self.status["condition"][-1][i + 1] - 1, self.sentence_index))
                    logging.debug(
                        "due to endif sentence, "
                        "the connection between %s and %s should be made when handling %s whose index is %s"
                        % (self.status["condition"][-1][i + 1] - 1,
                           self.sentence_index,
                           self.result,
                           self.sentence_index))

                present_condition = self.status['condition'][-1].copy()
                self.status['condition'].pop(-1)

                # here are some fix method, might be ugly
                # after running endif, the other option args related to this if condition should be cleared
                # similar to local var in c

                def preprocess(order):
                    for i1 in present_condition:
                        if i1 in order.other_option:
                            while True:
                                try:
                                    order.other_option.remove(i1)
                                except ValueError:
                                    break

                self.result = preprocess

        def _translate(self):
            # sentence --> function
            if not self.result:
                return
            # for the preprocess function
            if callable(self.result):
                f = MyFunction(self.result, ("self",), (), self.sentence, self.sentence_index + 1)
                f.preprocess = 1
                self.status["line"].append(f)
                return
            # translate
            loop = asyncio.get_event_loop()
            single_word = self.result.split(' ')
            finding_attr = []
            return_attr = set()
            order_sentence = ''
            for item in single_word:
                if item == '':
                    continue
                if item[0] == '*':
                    finding_attr.append(item[1:])
                    order_sentence = order_sentence + '* '
                elif item[0] == "&":
                    return_attr.add(item[1:])
                    order_sentence = order_sentence + '& '
                else:
                    order_sentence = order_sentence + item + ' '
            order_sentence = order_sentence.rstrip()
            if order_sentence not in loop.dictionary:
                raise ValueError('the sentence \'%s\' cannot be translated ' % self.result)
            fn = loop.dictionary[order_sentence]
            logging.debug("when translate %s, return is %s, args is %s, function is %s" %
                          (self.sentence, return_attr, finding_attr, fn.__name__))
            self.status["result"].update(return_attr)
            self.status["args"].update(finding_attr)
            self.status["line"].append(MyFunction
                                       (fn, finding_attr, return_attr, self.sentence, self.sentence_index + 1))

    def __new__(cls, name, bases, attrs):

        if name == 'Order':
            return type.__new__(cls, name, bases, attrs)

        lib = ctypes.cdll.LoadLibrary("./tree.so")
        lib.create_new_order(attrs["instruction"])
        attrs["lib"] = lib

        return type.__new__(cls, name, bases, attrs)


class Order(metaclass=NumberVectorMetaclass):
    def __init__(self, **kwargs):
        self.line = copy.deepcopy(self.pre_line)
        self.input_args = kwargs
        self.other_option = []
        self.present_index = -1
        self.args_dict = self.input_args
        self.args_dict["self"] = self
        self.exception = []
        self.watcher = {}
        try:
            loop = asyncio.get_running_loop()
        except BaseException:
            loop = asyncio.get_event_loop()
        loop.create_task(self._run())

    async def _run(self):
        while True:
            try:
                coro = self.next_line()
            # this means line has been run completely, that is, order is done
            except StopIteration:
                return
            # it means the code in next_line go wrong
            except ConditionWrongException as e:
                if self.present_index == self.other_option[-1]:
                    # that is to say, you need not to roll back, get next id instead
                    self.line[self.present_index].get_later_id()
                    continue
                self.present_index = self.other_option[-1]
                self.other_option.pop(-1)
                logging.info("At %s, %s, rollback to %s (proposal %s, %s)whose index is %s"
                             % (self,
                                e,
                                self.line[self.present_index].__name__,
                                self.line[self.present_index].proposal_sentence,
                                self.line[self.present_index].row,
                                self.present_index))
                continue

            except OrderFailedException as e:
                logging.warning("At %s, %s" % (self, e))
                for e in self.exception:
                    raise e

            except BaseException as e:
                raise e
                logging.warning("At %s, %s" % (self, e))
                self.set_exception_to_present_line(e)

            if not asyncio.iscoroutine(coro):
                # some function may not be coroutine
                self.set_result_to_present_line(coro)
                continue

            try:
                r = await coro
                self.set_result_to_present_line(r)

            except BaseException as e:
                # this mean the code has something wrong
                logging.warning("At %s,when handeling %s (proposal %s %s) %s"
                                % (self,
                                   self.line[self.present_index].__name__,
                                   self.line[self.present_index].proposal_sentence,
                                   self.line[self.present_index].row,
                                   e))
                self.set_exception_to_present_line(e)

    def next_line(self):
        # here to run the first function
        while True:
            fn = self.line[self.present_index]
            try:
                index = fn.get_later_id()
                next_fn = self.line[index]
                logging.debug("At %s, after running %s at %s, we are running function %s whose index is %s" %
                              (self, fn.__name__, self.present_index, next_fn.__name__, index))
                self.present_index = index
                if len(next_fn.later_id) - next_fn.present_index > 1:
                    self.other_option.append(self.present_index)
                    logging.debug("find another way %s when handling %s", next_fn.later_id, next_fn.proposal_sentence)
                args = []
                try:
                    for i in next_fn.inputer:
                        args.append(self.args_dict[i])
                except KeyError:
                    raise KeyError("when handling %s (proposal: %s, %s)"
                                   "%s not in %s" %
                                   (next_fn.__name__, next_fn.proposal_sentence, next_fn.row, i, self.args_dict))
                return next_fn(*args)
            except ConditionWrongException as e:
                raise e
            except IndexError:
                # you cannot get later id in next_fn!
                if self.present_index == len(self.line) - 2:
                    # that is over
                    raise StopIteration
                try:
                    logging.debug("At %s, when handling %s (proposal: %s, %s) at %s, rollback index %s" %
                                  (self,
                                   self.line[self.present_index].__name__,
                                   self.line[self.present_index].proposal_sentence,
                                   self.line[self.present_index].row,
                                   self.present_index,
                                   self.other_option[-1]))

                    self.present_index = self.other_option[-1]
                except IndexError:
                    # ok, now no way to go
                    if set(self.exception):
                        # there are other exceptions
                        raise OrderFailedException
                    else:
                        # done!
                        raise StopIteration

    def set_result_to_present_line(self, result):
        rs = self.line[self.present_index].results
        # # similar to python return type
        try:
            self.watcher[self.present_index].set_result(None)
        except Exception as e:
            pass
        logging.debug("at %s, after running %s (proposal %s %s) add %s (refer to %s) to %s" %
                      (self,
                       self.line[self.present_index].__name__,
                       self.line[self.present_index].proposal_sentence,
                       self.line[self.present_index].row,
                       rs,
                       result,
                       self.args_dict))

        if len(rs) == 1:
            self.args_dict[list(rs)[0]] = result
        else:
            for i in range(len(rs)):
                self.args_dict[rs[i]] = result[i]

    def set_exception_to_present_line(self, e):
        self.exception.append(e)

    def set_watcher(self, index_list):
        loop = asyncio.get_event_loop()
        for i in index_list:
            self.watcher[i] = loop.create_future()
        return self.watcher

class EventLoopPolicy(asyncio.DefaultEventLoopPolicy):
    """
        define start method as the start of order, followed by metaclass
        define dictionary
        define queues for thread, process, and network
        define the order protocol
    """

    def get_event_loop(self):
        try:
            loop = super().get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()

        asyncio.set_event_loop(loop)
        return loop


asyncio.set_event_loop_policy(EventLoopPolicy())
