from termcolor import colored

class File:
    def __init__(self, name, content="", parent=None):
        if not name.endswith(".txt"):
            raise ValueError("File name must end with .txt")
        self.name = name
        self.content = content
        self.parent = parent
        self.size = len(content)

    def append(self, new_content):
        self.content += "" + new_content
        self.size += len(new_content) + 1

    def edit_line(self, edited_line, edited_content):
        content_list = self.content.splitlines()
        if 0 <= edited_line - 1 < len(content_list):
            content_list[edited_line-1] = edited_content
            self.content = '\n'.join(content_list)
            self.size = len(self.content)
        else:
            print("your line does not exist ! ")

    def deline(self, del_line):
        content_list = self.content.splitlines()
        if 0 <= del_line - 1 < len(content_list):
            content_list.pop(del_line - 1)
            self.content = '\n'.join(content_list)
            self.size = len(self.content)
        else:
            print("your line does not exist ! ")

    def cat(self):
        if self.content:
            print(self.content)
        else:
            print("your file is empty! ")

    def get_size(self):
        return self.size


class Directory:
    def __init__(self, name, parent=None):
        self.name = name
        self.contents = {}
        self.parent = parent



class VirtualFileSystem:
    def __init__(self):
        self.root = Directory("root")
        self.current = self.root
        self.path = ["root"]

    def mkdir(self,name,path=""):
        new_dir = Directory(name, self.current)
        if path == "":
            self.current.contents[name] = new_dir
        else:
            path.contents[name] = new_dir

    def cd(self,path):
        if path == "..":
            if self.current.parent is not None:
                self.current = self.current.parent
                self.path.pop()      
        else:
            self.current = self.current.contents[path]
            self.path.append(path)

    def ls(self):
        for dirc in self.current.contents :
            print(colored(dirc,"blue"),end="\t")
        print()

    def rm(self, path):
        target = self._path_parser(path)
        if target:
            if isinstance(target, Directory):
                target.contents.clear()
            if target.name in target.parent.contents:
                del target.parent.contents[target.name]
            else:
                print("Path does not exist or is invalid.")
        else:
            print("Invalid path.")

    def cp(self, source_path, destination_path):
        source = self._path_parser(source_path)
        destination = self._path_parser(destination_path)

        if source and destination and isinstance(destination, Directory):
            if isinstance(source, Directory):
                deep_copy = Directory(source.name + "_copy", parent=destination)
                deep_copy.contents = {name: item for name, item in source.contents.items()}
            else:
                deep_copy = File(source.name.replace(".txt", "") + "_copy.txt", content=source.content, parent=destination)
            destination.contents[deep_copy.name] = deep_copy
        else:
            print("Invalid source or destination path.")

    def mv(self, source_path, destination_path):
        source = self._path_parser(source_path)
        destination = self._path_parser(destination_path)

        if source and destination and isinstance(destination, Directory):
            if source.name in source.parent.contents:
                del source.parent.contents[source.name]
            source.parent = destination
            destination.contents[source.name] = source
        else:
            print("Invalid source or destination path.")

    def new_file_txt(self, path):
        target = self._path_parser(path)
        if target and isinstance(target, File):
            print("Enter new content for the file (type 'EOF' on a new line to finish):")
            new_content = []
            while True:
                line = input()
                if line == "EOF":
                    break
                new_content.append(line)
            target.content = "\n".join(new_content)
            target.size = len(target.content)
        else:
            print("Invalid path or the specified path is not a file.")

    def touch(self, path_and_name):
        if "/" in path_and_name:
            *path_parts, file_name = path_and_name.split("/")
            folder = self._path_parser("/".join(path_parts))
        else:
            folder = self.current
            file_name = path_and_name

        if not file_name.endswith(".txt"):
            raise ValueError("File name must end with .txt")

        if folder and isinstance(folder, Directory):
            new_file = File(file_name, "", folder)
            folder.contents[file_name] = new_file
        else:
            print("Invalid path or folder does not exist.")

    def rename(self, path, new_name):
        target = self._path_parser(path)
        if target and target.name in target.parent.contents:
            if "/" in new_name:
                print("Invalid name: '/' is not allowed in names.")
                return
            target.parent.contents[new_name] = target.parent.contents.pop(target.name)
            target.name = new_name
        else:
            print("Invalid path or the specified path does not exist.")

    def append_text(self, path):
        target = self._path_parser(path)
        if target and isinstance(target, File):
            print("Enter text to append to the file (type 'EOF' on a new line to finish):")
            new_content = []
            while True:
                line = input()
                if line == "EOF":
                    break
                new_content.append(line)
            target.append("\n".join(new_content))
        else:
            print("Invalid path or the specified path is not a file.")

    def edit_line(self, path, line_number, new_content):
        target = self._path_parser(path)
        if target and isinstance(target, File):
            target.edit_line(line_number, new_content)
        else:
            print("Invalid path or the specified path is not a file.")

    def delete_line(self, path, line_number):
        target = self._path_parser(path)
        if target and isinstance(target, File):
            target.deline(line_number)
        else:
            print("Invalid path or the specified path is not a file.")

    def cat(self, path):
        target = self._path_parser(path)
        if target and isinstance(target, File):
            target.cat()
        else:
            print("Invalid path or the specified path is not a file.")

    def _path_parser(self, path):
        if path.startswith("/"):
            folder = self.root
            for name in path.strip("/").split("/"):
                if name in folder.contents:
                    folder = folder.contents[name]
                else:
                    print(f"Invalid path: {path}")
                    return None
            return folder
        elif path == "..":
            return self.current.parent if self.current.parent else self.current
        elif path in self.current.contents:
            return self.current.contents[path]
        else:
            print(f"Invalid path: {path}")
            return None

class CommandPrommt:
    def __init__(self, user, file_system: VirtualFileSystem):
        self.commands = {
            "mkdir": file_system.mkdir,
            "cd": file_system.cd,
            "ls": file_system.ls,
            "touch": file_system.touch,
            "rm": file_system.rm,
            "rename": file_system.rename,
            "cp": file_system.cp,
            "mv": file_system.mv,
            "nwfiletxt": file_system.new_file_txt,
            "appendtxt": file_system.append_text,
            "editline": file_system.edit_line,
            "deline": file_system.delete_line,
            "cat": file_system.cat,
        }
        self.user = user
        self.file_system = file_system

    def _path_parser(self, path):
        if path[0] == "/":
            folder = self.file_system.root
            for name in (path.split("/"))[1:]:
                folder = folder.contents[name]
            return folder
        else:
            return path

    def read_line(self):
        command = input(colored(f"{'/'.join(self.file_system.path)} {self.user} >", "green"))
        command = command.split(" ")
        func = self.commands.get(command[0])
        if func:
            if len(command) == 1:
                func()
            elif len(command) == 2 and command[0] == "cat":
                func(self._path_parser(command[1]))
            elif len(command) == 2:
                func(self._path_parser(command[1]))
            elif len(command) == 3 and command[0] == "deline":
                func(self._path_parser(command[1]), int(command[2]))
            elif len(command) == 4 and command[0] == "editline":
                func(self._path_parser(command[1]), int(command[2]), " ".join(command[3:]))
            else:
                func(self._path_parser(command[1]), self._path_parser(command[2]))
        else:
            print("Invalid Command!")

if __name__ == "__main__":
    file_system = VirtualFileSystem()
    command_prommt = CommandPrommt("Admin",file_system)
    while True:
        command_prommt.read_line()
