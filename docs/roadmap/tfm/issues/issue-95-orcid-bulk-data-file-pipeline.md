# Issue 95 - ORCID Bulk Data File Pipeline

## Summary

Download and filter the ORCID public data file to a manageable working
volume subset. Second data-source issue of TFM epic phase 2.

## Original Goal

Obtain a real, sizeable ORCID dataset as the platform's genuine "big data"
volume source, instead of relying on synthetic data for scale.

## Original Plan

- verify the current official download location and format for the ORCID
  Public Data File before writing any code against it (it has moved hosting
  providers over the years, per the epic's own caution)
- download the file (or the relevant portion of it)
- implement a filter to produce the working subset (candidate filters: a
  Spain-affiliated employment/education entry, or a field/keyword filter),
  bounding the volume used day-to-day
- store the filtered subset ready for bronze landing (issue `#97`)

## Adjustments Made During Implementation

Not applicable yet; no implementation has started.

## Implementation Performed

Not applicable yet; no implementation has started.

## Verification

Planned: the downloaded file parses correctly; the filter produces a subset
of the expected order of magnitude, not the full multi-million-record file.
Not yet executed.

## Findings

Not applicable yet.

## Known Limitations

Not applicable yet. Per the epic, processing the full public data file at
web scale is explicitly deferred to future work; only a filtered subset is
in scope here.

## Impact On Future Issues

Feeds issue `#97` (bronze landing) as the ORCID bulk source, and indirectly
issue `#101` (benchmark), which needs a real base volume to scale from.

## Status

`Planned`
