# 🚀 Automated Weekly Evaluation Pipeline

## Quick Start

### Run the Pipeline

```bash
# Test run (dry run mode)
python pipeline/master.py

# Full evaluation
# Edit pipeline/config.yaml and set dry_run: false
python pipeline/master.py
```

### Configuration

Edit `pipeline/config.yaml` to customize:
- **Models to evaluate**: Update `portkey_id` values
- **Questions per category**: Adjust `questions_per_category`
- **Schedule**: Set `day`, `hour`, `minute`
- **Notifications**: Enable email/Slack

### Directory Structure

```
pipeline/
├── master.py          # Main orchestrator
├── config.yaml        # Configuration
└── scheduler/         # Scheduling scripts

logs/weekly/           # Evaluation logs
└── YYYY-MM-DD/
    ├── pipeline.log
    ├── test_gemini.log
    ├── test_gpt.log
    ├── test_claude.log
    ├── debate_results.json
    ├── rankings.json
    └── report.txt

archive/evaluations/   # Archived results
```

### Features

✅ **Automated Evaluation**: Runs all models automatically  
✅ **Debate Mechanism**: Multi-judge scoring  
✅ **Auto-Routing**: Updates to best models  
✅ **Version Tracking**: Uses latest model versions  
✅ **Notifications**: Email/Slack alerts  
✅ **Archival**: Keeps last 12 weeks of results  

### Development

1. **Test Mode**: Set `dry_run: true` in config
2. **Run Once**: `python pipeline/master.py`
3. **Schedule**: See `pipeline/scheduler/` for setup

### Next Steps

1. ✅ Basic pipeline working
2. ⏳ Implement version checker
3. ⏳ Connect to actual evaluation scripts
4. ⏳ Set up weekly scheduler

See `pipeline_plan.md` for full roadmap!
