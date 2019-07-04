# decorator for class base view
# print which function or method is invoked
def which_invoked(decorator):

    def the_wrapper(*args, **kwargs):

        it_object = decorator
        print("<<< Початок", it_object, 'args', args)
        response = decorator(*args, **kwargs)
        print("Кінець", it_object, ' >>> kwargs', kwargs)
        return response

    return the_wrapper


# @ which_invoked # simple exemple
# def simple_function():
#     print("Middle")
#
#
# class SimpleClass:
#
#     @which_invoked
#     def simple_method(self):
#         print("method")
#
#
# simple_obj = SimpleClass()
# simple_function()
# simple_obj.simple_method()
