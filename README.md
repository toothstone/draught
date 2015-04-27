draught - come and get some beer
==================================

This project is a flask-based webserver originally developed by members of the 
student network Dresden [1] (project SIPA), adapted for ZAPF DD 2016 by the 
ZAPF-IT
 DD 
team.


Libraries required to run dev server
----------------------------------

Debian packages:
`apt-get install libldap2-dev libffi-dev libsasl2-dev libxml2-dev libxslt1-dev libmysqlclient-dev libpython2.7-dev`


Required format for the markdown files
----------------------------------
In the folder `content/` you can place markdown files to use them as *content pages* as well as *news*.
The folder structure has to look like this, following the conditions explained below:

    content
    ├── images
    │   ├── image.png
    │   └── logo.png
    ├── legal
    │   ├── impressum.de.md
    │   ├── impressum.en.md
    │   ├── index.de.md
    │   └── index.en.md
    ├── news
    │   ├── 2015-03-11-new_website.de.md
    │   ├── 2015-03-11-new_website.en.md
    │   ├── index.de.md
    │   └── index.en.md
    └── support
        ├── contacts.de.md
        ├── contacts.en.md
        ├── faq.de.md
        ├── faq.en.md
        ├── index.de.md
        └── index.en.md

The *navigation bar* is built by scanning every directory for `*.md`-files.
 Directories containing the latter are then expected to contain an index file for every language code, e.g. `index.en.md`
 These index files decide whether it will appear in the navigation bar and which title it will be displayed with.
 
The index files have to contain certain metadata in the form `property: value`. This metadata section is terminated by an empty line (`\n\n`)
* To *not* include a folder in the menu, set `index: false`, as you will need for the `news/` folder(!).
* To *include* a folder, set the title of the navigation bar with `name:` as well as its position with `rank`.
 Do not forget to set `index: true` explicitly.
 
If the parameter `index` does not exist, the corresponding folder will not appear in the navigation bar, although every folder containing a markdown file *must* contain an `index.xx.md` file.

The markdown files must have a header in the same fashion as the index files. A complete .md file can look like this:

    title: Stuff
    author: alice
    date: 2015-03-27
    glyphicon: glyphicon-user
    
    ### Stuff
    #### Part 1
    
    To do stuff, you have to do stuff first.

Another possibility is to include hyperlinks, which only have a metadata section:

    title: Awesome page
    glyphicon: glyphicon-tower
    link: http://http://www.awesome-page.com/
    rank: 1

[1] agdsn.de