import os
import sys

from mwr.common import cli
from mwr.droidhg.repoman.installer import ModuleInstaller
from mwr.droidhg.repoman.remotes import Remote, UnknownRemote
from mwr.droidhg.repoman.repositories import Repository, NotEmptyException, UnknownRepository
from mwr.droidhg.repoman.repository_builder import RepositoryBuilder

class ModuleManager(cli.Base):
    """
    mercury module [COMMAND]
    
    Run the Mercury Module and Repository Manager.

    The Repository Manager handles Mercury modules and module repositories.
    """

    def __init__(self):
        cli.Base.__init__(self)
        
        self._parser.add_argument("options", nargs='*')
        
    def do_install(self, arguments):
        """install a new module"""
        
        repository = self.__choose_repo()
        
        if repository != None:
            installer = ModuleInstaller(repository)
            modules = installer.install(arguments.options)
                        
            print
            print "Successfully installed %d modules." % len(modules['success'])
            print "Failed to install %d:" % len(modules['fail'])
            for module in modules['fail']:
                print "  %s" % module
                print "    %s" % modules['fail'][module]
            print
        
    def do_remote(self, arguments):
        """manage the source repositories, from which you install modules"""
        
        RemoteManager().run(arguments.options)
        
    def do_repository(self, arguments):
        """manage module repositories, on your local system"""
        
        RepositoryManager().run(arguments.options)
        
    def do_search(self, arguments):
        """search for modules"""

        self.__search_remotes(len(arguments.options) > 0 and arguments.options[0] or "")
    
    def __choose_repo(self):
        """
        Return the path of a repository, either the only repo or presenting the user
        with a choice.
        """
        
        repositories = Repository.all()
        
        if len(repositories) == 1:
            return repositories[0]
        elif len(repositories) == 0:
            print "You do not have a Mercury module repository. Please create one, then try again."
            
            return None
        else:
            print "You have %d Mercury module repositories. Which would you like to install into?\n" % len(repositories)
            for i in range(len(repositories)):
                print "  %5d  %s" % (i+1, repositories[i])
            print
            
            while(True):
                print "repo>",
                try:
                    idx = int(raw_input().strip())
                
                    if idx >= 1 and idx <= len(repositories):
                        print
                        
                        return repositories[idx-1]
                    else:
                        raise ValueError(idx)
                except ValueError:
                    print "Not a valid selection. Please enter a number between 1 and %d." % len(repositories)
    
    def __search_remotes(self, term):
        """
        Search for modules, on remote repositories.
        """
        
        installer = ModuleInstaller(None)
        modules = installer.search_index(term)
        
        if len(modules) > 0:
            for module in modules:
                print module
            print
        else:
            print "No modules found.\n"


class RemoteManager(cli.Base):
    """
    mercury module remote [COMMAND] [OPTIONS]
    
    Run the remote part of the Mercury Module and Repository Manager.
    """

    def __init__(self):
        cli.Base.__init__(self)
        
        self._parser.add_argument("options", nargs='*')
        
    def do_create(self, arguments):
        """create a new remote module repository"""
        
        if len(arguments.options) == 1:
            url = arguments.options[0]

            Remote.create(url)
            
            print "Added remote: %s.\n" % url
        else:
            print "usage: mercury module remote create http://path.to.repository/\n"
    
    def do_delete(self, arguments):
        """remove a remote module repository"""
        
        if len(arguments.options) == 1:
            url = arguments.options[0]
            
            try:
                Remote.delete(url)
                
                print "Removed remove %s.\n" % url
            except UnknownRemote:
                print "The target (%s) is not a remote module repository.\n" % url
        else:
            print "usage: mercury module remote delete http://path.to.repository/\n"
        
    def do_list(self, arguments):
        """shows a list of all remotes"""
        
        print "Remote repositories:"
        for url in Remote.all():
            print "  %s" % url
        print
                
        
class RepositoryManager(cli.Base):
    """
    mercury module repository [COMMAND] [OPTIONS]
    
    Run the repository part of the Mercury Module and Repository Manager.

    The Repository Manager handles Mercury modules and module repositories.
    """

    def __init__(self):
        cli.Base.__init__(self)
        
        self._parser.add_argument("options", nargs='*')
        
    def do_create(self, arguments):
        """create a new Mercury module repository"""
        
        if len(arguments.options) == 1:
            path = arguments.options[0]
            
            try:
                Repository.create(path)
                
                print "Initialised repository at %s.\n" % path
            except NotEmptyException:
                print "The target (%s) already exists.\n" % path
        else:
            print "usage: mercury module repository create /path/to/repository\n"
    
    def do_delete(self, arguments):
        """remove a Mercury module repository"""
        
        if len(arguments.options) == 1:
            path = arguments.options[0]
            
            try:
                Repository.delete(path)
                
                print "Removed repository at %s.\n" % path
            except UnknownRepository:
                print "The target (%s) is not a Mercury module repository.\n" % path
        else:
            print "usage: mercury module repository delete /path/to/repository\n"
                
    def do_disable(self, arguments):
        """hide a Module repository, without deleting its contents"""
        
        if len(arguments.options) == 1:
            path = arguments.options[0]
            
            try:
                Repository.disable(path)
                
                print "Hidden repository at %s.\n" % path
            except UnknownRepository:
                print "The target (%s) is not a Mercury module repository.\n" % path
        else:
            print "usage: mercury module repository disable /path/to/repository\n"
    
    def do_enable(self, arguments):
        """enable a previously disabled Module repository"""
        
        if len(arguments.options) == 1:
            path = arguments.options[0]
            
            try:
                Repository.enable(path)
                
                print "Enabled repository at %s.\n" % path
            except UnknownRepository:
                print "The target (%s) is not a Mercury module repository.\n" % path
        else:
            print "usage: mercury module repository enable /path/to/repository\n"
        
    def do_list(self, arguments):
        """list all repositories, both local and remote"""
        
        self.__list_repositories()
        
    def do_make(self, arguments):
        """build a repository, from a Python package"""
        
        if len(arguments.options) != 1:
            print "you must specify the target"
            sys.exit(-1)
            
        RepositoryBuilder(os.getcwd(), arguments.options[0]).build()
        
    def __list_repositories(self):
        """
        Print a list of Mercury repositories (a) on the local system, and
        (b) registered as remotes.
        """
        
        print "Local repositories:"
        for repo in Repository.all():
            print "  %s" % repo
        print
        