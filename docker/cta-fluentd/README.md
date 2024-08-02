Description of files

```
Containerfile                   Builds the fluentd image used on OKD

Containerfile.logs              Builds the fluentd image used on taped and frontend

build_images_Fluentd.sh         Builds and uploads both images

cta-public-5-alma9.repo         Normal repo file to use

cta-public-5-test-alma9.repo    Current repo file to get 5.10.11 which has the tape format type in the response

entrypoint.sh                   Entrypoint for Containerfile

frontend-td-agent.conf          fluentd config file for frontend logs

run_frontend_fluentd.sh         Run fluentd to collect frontend logs

run_taped_fluentd.sh            Run fluentd to collect taped logs

taped-td-agent.conf             fluentd config file for taped logs

td-agent-ctaadmin.conf          Old

td-agent-file-taped.conf        Old

td-agent-lsk-taped.conf         Old

td-agent-lssr-taped.conf        Old

td-agent-taped.conf             Old

td-agent.conf                   Old
```
