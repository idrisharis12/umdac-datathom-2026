#!/usr/bin/env bash
set -e
echo "Reassembling swift_umdac_datathon_2026_fictitious_payment_data.csv from split parts..."
cat swift_umdac_datathon_2026_fictitious_payment_data.csv.part_* > swift_umdac_datathon_2026_fictitious_payment_data.csv
echo "Verification:"
ls -lh swift_umdac_datathon_2026_fictitious_payment_data.csv
echo "Reassembly successfully completed."
