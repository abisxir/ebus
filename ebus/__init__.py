__version__ = '0.1.2'
__author__ = 'Abi Mohammadi'

import asyncio
import inspect


__handlers = {}


class EventContext(dict):
    def __init__(self):
        self.__stop = False

    def stop(self):
        self.__stop = True

    @property
    def keep_going(self):
        return not self.__stop


def is_registered_before(event_type, new_handler):
    olds = __handlers[event_type]
    for handler, pass_context_as_args, pass_context_as_kwargs, run_async, in olds:
        if handler is new_handler:
            return True
    return False


def is_registered_for_other_events(new_handler):
    for event_type in __handlers:
        if is_registered_before(event_type, new_handler):
            return True


def add_handler(event_type, handler):
    if event_type not in __handlers:
        __handlers[event_type] = []

    if is_registered_for_other_events(handler):
        ValueError('Function [] is already registered for event []'.format(handler, event_type))

    if not is_registered_before(event_type, handler):
        params = inspect.getfullargspec(handler)
        pass_context_as_args = len(params.args) > 1 or params.varargs is not None
        pass_context_as_kwargs = not pass_context_as_args and params.varkw is not None
        run_async = inspect.iscoroutinefunction(handler)
        __handlers[event_type].append((handler, pass_context_as_args, pass_context_as_kwargs, run_async))


def __run_handler(ctx, event, handler, pass_context_as_args, pass_context_as_kwargs):
    if pass_context_as_args:
        return handler(event, ctx)
    elif pass_context_as_kwargs:
        return handler(event, ctx=ctx)
    else:
        return handler(event)

async def __run_slots_async(slots, event):
    ctx = EventContext()
    for slot in slots:
        if ctx.keep_going:
            handler, pass_context_as_args, pass_context_as_kwargs, run_async, = slot
            if run_async:
                await __run_handler(ctx, event, handler, pass_context_as_args, pass_context_as_kwargs)
            else:
                __run_handler(ctx, event, handler, pass_context_as_args, pass_context_as_kwargs)
        else:
            break

def __run_slots(slots, event):
    ctx = EventContext()
    for slot in slots:
        if ctx.keep_going:
            handler, pass_context_as_args, pass_context_as_kwargs, run_async, = slot
            __run_handler(ctx, event, handler, pass_context_as_args, pass_context_as_kwargs)
        else:
            break

def emit(event):
    event_type = type(event)
    slots = __handlers.get(event_type)
    if slots is not None and len(slots) > 0:
        __run_slots(slots, event)

async def emit_async(event):
    event_type = type(event)
    slots = __handlers.get(event_type)
    if slots is not None and len(slots) > 0:
        await __run_slots_async(slots, event)


def handle(event_type, **kwargs): 
    def wrapper(func): 
        """This function wraps the handler execution.

        :return: return event handler function
        :rtype: function
        """
        add_handler(event_type, func)
        return func
    
    return wrapper


