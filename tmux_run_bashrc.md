# Tmux running bashrc

Ubuntu sources bashrc everytime tmux launches, or splits windows. It could makes some results like $PATH repeating.

Not sure why, [reference](https://unix.stackexchange.com/questions/320465/new-tmux-sessions-do-not-source-bashrc-file)

## Workaround

when sourcing files in bashrc, do like this:

```shell
if ! command -v petalinux-util &> /dev/null; then
  source ~/petalinux/settings.sh > /dev/null
  source ~/opt/Vivado/2021.2/settings64.sh > /dev/null
fi
```
