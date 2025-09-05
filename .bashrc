# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

# User specific environment
if ! [[ "$PATH" =~ "$HOME/.local/bin:$HOME/bin:" ]]
then
    PATH="$HOME/.local/bin:$HOME/bin:$PATH"
fi
export PATH

# Uncomment the following line if you don't like systemctl's auto-paging feature:
# export SYSTEMD_PAGER=

# User specific aliases and functions

# 登录时自动启动claude
if [[ $- == *i* ]] && [[ -z "$CLAUDE_STARTED" ]]; then
    export CLAUDE_STARTED=1
    echo "启动Claude Code..."
    claude --dangerously-skip-permissions
fi
