import my_database
import sys


def execute_command(command, args, file_name):
    if file_name is None:
        data_base = my_database.myDataBase()
    else:
        data_base = my_database.myDataBase(file_name)
    if command == 'sort_by':
        if args:
            data_base.sort_by(args[0])
    elif command == 'filter_by':
        data_base.filter_by(args)
    elif command == 'compare':
        if len(args) < 3:
            print('At least 3 arguments are needed.')
            return
        data_base.compare_by(args)
    elif command == 'add':
        for title in args:
            data_base.add_movie(title)
    elif command == 'highscores':
        data_base.get_highscores()
    elif command == 'load_data':
        data_base.load_data(args)
    else:
        print(f'{command} command not found.')


def create_commands_list(args):
    file_name = None
    arg_list = []
    command = ''
    for arg in args:
        if arg[:2] == '--':
            if command != '':
                if command == 'set_file_name':
                    file_name = arg_list[0]
                else:
                    execute_command(command, arg_list, file_name)
                arg_list.clear()
            command = arg[2:]
            arg_list.clear()
        elif command != '':
            arg_list.append(arg)
        else:
            print(f'{arg} command not found.')
    if command != '':
        if command != 'set_file_name':
            execute_command(command, arg_list, file_name)


create_commands_list(sys.argv[1:])
