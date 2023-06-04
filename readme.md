# Realms Data Pack Development Kit

*Currently, this tool is only supported on Windows. It is possible to get it running on other OS's, but you will experience issues.*

## Installation
1. First you will need a semi-recent version of Panda3D. If you don't have one downloaded already,
you can find one [here](https://www.panda3d.org/download/).
2. Clone this repository
   * You can do this by the following methods
     1. [Clone it through GitHub by clicking here](x-github-client://openRepo/https://github.com/ttoff/dpdk) if you have [Github Desktop](https://desktop.github.com/)
     2. Running `git clone https://github.com/ttoff/dpdk.git` in your terminal in a new folder
     3. Pressing Download Zip (NOT recommended, as you will have to manually redownload each time there's an update)
3. Open `run.cmd` in your text editor of choice and edit the `set PANDA_PATH=` to point to your Panda3D installation directory
4. Run `run.cmd`

## Tutorial

* [Creating a Data Pack](#creating-a-data-pack)
* [Overriding a Cog Appearance](#overriding-a-cog-appearance)
* [Changing Cog Quotes](#changing-cog-quotes)
* [Changing Cog Spawns](#changing-cog-spawns)
* [Building and Distributing your pack](#building-and-distributing-your-pack)

## Creating a Data Pack
1. Open the Data Pack Development Kit
2. Press New Pack

![](https://toontownrealms.com/images/dpdktutorial/create_01.jpg)
3. Fill out all the fields (all are required)
4. Press Create

![](https://toontownrealms.com/images/dpdktutorial/create_02.jpg)

## Overriding a Cog Appearance
1. Create a pack, or open an already existing one
2. In the Cog Appearances Tab, click New Override

![](https://toontownrealms.com/images/dpdktutorial/appearance_01.jpg)

3. Choose a base game Cog you want to override

![](https://toontownrealms.com/images/dpdktutorial/appearance_02.jpg)

4. You can now edit various aspects of the Cog's Body through the Body tab
   * *Note, all changes are saved automatically*

![](https://toontownrealms.com/images/dpdktutorial/appearance_03.jpg)

5. And edit the head through the Head tab

![](https://toontownrealms.com/images/dpdktutorial/appearance_05.jpg)

On the head tab, you can modify existing head parts, replace them, add new ones, or remove them.

6. You can add a new part by pressing the Add Head Part button

![](https://toontownrealms.com/images/dpdktutorial/appearance_06.jpg)

7. You can delete head parts by pressing the x button


![](https://toontownrealms.com/images/dpdktutorial/appearance_07.jpg)

8. You can edit the Cog's name in the Info tab

![](https://toontownrealms.com/images/dpdktutorial/appearance_08.jpg)

9. When you're done, press the Back to Cog list button

![](https://toontownrealms.com/images/dpdktutorial/appearance_09.jpg)

## Changing Cog Quotes
This feature of Data Packs is currently not available in the Data Pack Development Kit

## Changing Cog Spawns
This feature of Data Packs is currently not available in the Data Pack Development Kit

## Building and Distributing your pack
1. Open your pack
2. In the Share menu, press Compile Pack

![](https://toontownrealms.com/images/dpdktutorial/build_01.jpg)

3. When the build is complete, your file browser will open and show you the finished file.
4. You can now put it in your game directory, or share it with others.