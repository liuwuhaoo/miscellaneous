#PATH Env Pollution

enviroments: `Alacritty`, `zsh`, `tmux`, `conda`

__Pollution Cases:__
- Repetitive paths in PATH
- some paths are overridden, for example, `which python` results in `/usr/bin/python3` rather `/.../anaconda3/bin`, and the error `ModuleNotFoundError: No module named ...` could happen.


__Reasons:__
The zsh shell files run in order of:

```
/etc/zshenv
~/.zshenv
/etc/zprofile
~/.zprofile
/etc/zshrc
~/.zshrc
/etc/zlogin
~/.zlogin
```
These files change the $PATH.

- PATH accidentally polluted by all kinds of tools
- when a tmux session starts, the shell files runs again and results in repetition and overrides.


__Solution:__

One quick way to find how these files change the PATH is `echo $PATH` and the start and the end of the files. Identify the locations where the PATH has been incorrectly modified and correct them.

Note that when a Alacritty window is started, not all the shell files run. Depends on login or non-login shell is opened (check alacritty configuration `Shell`)

For tmux sessions, there is no way(?) to stop it source those shell files because it start a new session. Tmux start a new non-login shell by default, if not, [set it manually](https://superuser.com/questions/1330824/how-to-stop-tmux-from-launching-login-shells). This cannot stopping the sourcing of `/etc/zshrc`, `~/.zshrc` and (maybe) others. In that case, set PATH in this files when it is not in tmux enviroments.

```language=Shell
if ! [ -n "$TMUX" ]; then
    export PATH = ...
fi
```

__Best Bractice(?):__
- Carefully manually set PATH
- Try to set PATH in one single file, e.g. move all settings from `~/.zshenv` to `~/.zshrc`
- Set PATH like `if somepath not in PATH, PATH="somepath:$PATH"`


__Others:__
- `path_helper` in `/etc/zprofile` add paths in `/etc/paths` and `/etc/paths.d` to PATH.
