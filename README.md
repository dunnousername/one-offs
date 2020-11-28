# one-offs
A bunch of scripts and projects I don't intend to provide support for, but might be useful to some people.

Most of these projects will not have licensing information. In the event that a project isn't explicitly marked as having another license in any of the source files (or a README file if one exists), you can use it under the [Creative Commons 0](https://creativecommons.org/publicdomain/zero/1.0/) public-domain-equivalent license.

These files are provided **as-is**; I will not be providing support for them, and I will not be accepting requests to update any of the code. However, if you open a pull-request that fixes a given issue, I probably will accept it.

## Description of folders in src/
- scpwiki/ - stuff related to backing up the SCP Wiki
- ahkhide/ - an AutoHotKey script that toggles the visibility of all windows when you click the scroll wheel
- mcenchant/ - calculate the probability of getting an enchanted book with a certain enchantment from fishing with LotS 3. This hasn't been updated in a while so I can't recall if it works. Use with caution.
- skyblocklootkeys/ - program I used to determine the actual value of Skyblock.net lootkeys. Might be outdated, use with caution.
- simpletk/ - a small Python library used in some of my projects to make interfacing with Tkinter less painful.
- findserver/ - a program that sends a legacy (<=1.6.4) ping request to a Minecraft server to check it's status.
- redditdl/ - a tool to get a list of links to every image (and video?) in a list of subreddits using pushshift.io, then sort them into what can be downloaded by youtube_dl, gallery-dl, and a standard HTTP(S) downloader like aria2c.
- filterproxies/ - go through a list of HTTP(S) or SOCKS proxies and check them to see if they work.
- pseudoscience/ - a joke program that generates pseudoscientific claims using a context-free grammar. Similar to mathgen or scigen.
- hololivedl/ - a program I made for someone else to download Hololive streams from youtube. It might not work anymore, and it doesn't contain an updated list of channels; it checks every (few?) seconds if a channel is streaming, so leaving this on for too long will cause youtube to stop working on your network for a bit.