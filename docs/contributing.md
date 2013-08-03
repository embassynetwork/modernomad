## Tickets and Issues

If you're using the site and see bugs, usability issues, or have suggestions,
then [the issue
tracker](https://github.com/jessykate/modernomad/issues?state=open) is the best
place to submit them. Developers will get a notification, we can discuss the
issue or idea, and then turn that into an implementation plan. 

We use [Pivotal Tracker](https://www.pivotaltracker.com/s/projects/883046) for
our tickets. Pivotal Tracker is specifically for to-do items for the project. There's
design- documentation- and development-related tickets there, so plenty to
help out with if you are inclined. To make it easier to hook into the process,
there are a few specific labels worth explaining: 

* **Simple**: should be relatively simple to do. Good for new programmers,
  non-programmers, or people just getting farmiliar with the code base. 
* **New Functionality**: if you want the satisfaction of implementing something
  that will expose new functionality to users, look at these. They are usually
  a bit harder, but worth it. 
* **Orientation**: these tickets are a good way to get oriented with the codebase,
  usually because they involve looking through a lot of code in order to find
  specific lines that touch a specific field or model. They can be simple or
  more advanced. 
* **Standalone**: these features can be big or small but are relatively
  independent of most of the hairy underpinnings and interdependencies of
  different pieces of the code. For example, it might be building a
  visualization, or integrating a new 3rd party service into the
  site. 

Other labels indicate the area of functionality the task is related
to, such as 'reservations,' 'notifications,' 'sysadmin,' or 'frontend.'

## General process for making contributions

1. [Fork the code and make a local clone](https://help.github.com/articles/fork-a-repo)
1. Get your dev environment set-up (see [Environment Setup](environment-setup.md) and [How to Run](how-to-run.md)).
1. Choose a [ticket](https://www.pivotaltracker.com/s/projects/883046) of interest, and tell someone you are planning to work on it (either on the Pivotal Tracker project or even just by contacting [jessy](mailto:jessy@embassynetwork.com))
1. Create a [new git branch](https://github.com/Kunena/Kunena-Forum/wiki/Create-a-new-branch-with-git-and-manage-branches) for the task you're working on
1. Make your mods! Work on the task. 
1. Commit your changes and push them back to your repository. ([basic overview of commands](https://help.github.com/articles/create-a-repo))
1. [Submit a pull request](https://help.github.com/articles/using-pull-requests) back to the origin repository. 



