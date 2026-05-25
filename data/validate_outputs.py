def validate_outputs(outputs):
    for output in outputs:
        if "name" not in output or "rank" not in output or "function" not in output or "appearance" not in output or ("legion_count" not in output and "legion_count?" in output) or "conjuration_method" not in output or "experiment_refs" not in output:
            return False
        if "page/folio" not in output:
            return False

    for experiment in outputs:
        if "title" not in experiment or "materials" not in experiment or "procedure" not in experiment or "spirits_invoked" not in experiment:
            return False

    return True