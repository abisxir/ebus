# ebus

**ebus** is a minimalistic event bus for python. It does not need any 
initialization or sequence for register or raise events. 

There are two concepts inside, events and handlers. The subscribers register 
a handler for a type of event, that can be any type actually, then they recieve a signal when a publisher
emits this signal. 

**ebus** accepts to emit the signal if there is no subscriber. However,
if you want to handle the events correctly, you should register you handlers
before you raise the event.

## Installation

The easy way to install package is to use pip:

```bash
sudo pip install ebus
```

Alternatively, you can download it or clone it directly from github and then type:

```bash
git clone https://github.com/abisxir/ebus.git
cd ebus
sudo python setup.py install
```

## Usage

The simple way is just like this, define your event, register them using handle decorator 
and emit your events when it is required:

```python
import ebus

# This can be anything
class MyEvent:
    def __init__(self, message):
        self.message = message

# Handlers can listen to any type
@ebus.handle(MyEvent)
async def handle_my_event(e: MyEvent):
    print(e.message)

# When this call, all registered handlers will run
await ebus.emit_async(MyEvent('My async event happened.'))
```

If you like to handle it in synchronous way, **ebus** will take care of that also: 

```python
@ebus.handle(MyEvent)
def handle_my_event_sync(e: MyEvent):
    print('Handle the event in sync mode:', e.message)

ebus.emit(MyEvent('My event happened.'))
```

There is also an event context provided to pass data to the other events or stop the chain:

```python
@ebus.handle(MyEvent)
def handle_first(e: MyEvent, ctx: ebus.EventContext):
    print('I add something to context of ', e.message)
    # Here we can attach any information to context, the next handler will get it.
    ctx['extra'] = 'Extra info can be anything'

@ebus.handle(MyEvent)
def handle_second(e: MyEvent, ctx: ebus.EventContext):
    # Here we get the extra information
    print('There is something for me in ctx [{}].'.format(ctx['extra']))
    # We add another information to context
    ctx['something_else'] = 12

@ebus.handle(MyEvent)
def handle_third(e: MyEvent, ctx: ebus.EventContext):
    print('If something else[{}] is less than 10 I will stop.'.format(ctx['something_else']))
    # It will stop if something_else is less than 10
    if ctx['something_else'] < 10:
        ctx.stop()

@ebus.handle(MyEvent)
def handle_last(e: MyEvent, ctx: ebus.EventContext):
    # We will never reach here to print this, as long as we stop the event chain
    print('Never see this!!!, event process stopped.')

ebus.emit(MyEvent('My event happened.'))
```

You can also use **register_handler** to register event handlers:

```python
def handle_my_event(e: MyEvent):
    print(e.message)

# This will register the event handler.
ebus.add_handler(MyEvent, handle_my_event)

# Will run all the handlers registered for this event.
ebus.emit(MyEvent('Test adding handler'))
```

Also **ebus** prevents add a handler twice, it just ignores the second one.

```python
def handle_my_event(e: MyEvent):
    print(e.message)

# The first one registers correctly
ebus.add_handler(MyEvent, handle_my_event)

# This will get ignored by ebus
ebus.add_handler(MyEvent, handle_my_event)

ebus.emit(MyEvent('My event happened.'))
```
