FROM fedora:40

# пакеты
RUN dnf -y update && \
    dnf -y install python3 python3-pip sqlite bash ncurses && \
    dnf clean all

# flask
RUN pip3 install --no-cache-dir flask

# не-root пользователь dev с uid/gid 1000
RUN groupadd -g 1000 dev && useradd -m -u 1000 -g 1000 dev

USER dev
WORKDIR /workspaces/project