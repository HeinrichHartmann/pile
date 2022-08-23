#!/usr/bin/env bash

poetry run python -c 'from pile import srv; srv.main()' $@
