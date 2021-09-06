## Command (run workflow with luigi)
python -m luigi --module run Extract  --local-scheduler

## Call (run workflow with function call)
run_workflow("Invoice_28092018-171040.pdf")