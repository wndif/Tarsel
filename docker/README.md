# Licensed VCS inside Docker

Tarsel2 needs Synopsys VCS and URG. Both are commercial: no Synopsys
executable, PLI archive, or licence file is included in this repository or in
the image, and none is redistributed here.

The pattern is:

- the **image** holds the tool plus the runtime libraries VCS needs;
- the **Synopsys tree** lives in a private Docker volume the user provisions
  from an authorized installation;
- the **licence** is injected at run time through `LM_LICENSE_FILE`.

## 1. Provision the volume once

From a machine with a licensed installation:

```bash
docker volume create tarsel2_synopsys

docker run --rm \
    -v tarsel2_synopsys:/opt/synopsys \
    -v /path/to/your/synopsys:/from:ro \
    alpine sh -c "cp -a /from/. /opt/synopsys/"
```

Expected layout inside the volume:

```
/opt/synopsys/
├── vcs/O-2018.09-SP2/                 # adjust to your version
│   ├── bin/                           # vcs, urg, ...
│   └── linux64/...
└── verdi/Verdi_O-2018.09-SP2/share/PLI/VCS/linux64/
    ├── novas.tab
    └── pli.a
```

If your version differs, pass `-e VCS_HOME=/opt/synopsys/vcs/<your-version>`.

Verdi PLI is optional; set `verdi_pli` in the project yaml only if you build
with FSDB support.

## 2. Build the image

```bash
docker build -f docker/Dockerfile -t tarsel2:local .
```

## 3. Run

```bash
docker run --rm \
    -v "$PWD:/data" \
    -v tarsel2_synopsys:/opt/synopsys:ro \
    -e LM_LICENSE_FILE=27000@<your-license-server> \
    tarsel2:local localize --config examples/updown_counter/tarsel2.yaml
```

The licence server must be reachable from the container. Tarsel2 never writes
into `/opt/synopsys`; the volume is mounted read-only.

## Troubleshooting

| Symptom | Cause |
|---|---|
| `Cannot find VCS compiler ... linux/bin/vcs1` | 32-bit lookup; ensure `-full64` is in `vcs_options` and `VCS_HOME` points at your version |
| `Failed to obtain license` | licence server down or `LM_LICENSE_FILE` wrong; check with `lmstat` |
| `URG-NVAT No test found` | simulations ran without `-cm_name`; rerun the full pipeline |
| apt fails during build | host proxy forwarded into the build; the Dockerfile clears it already |
