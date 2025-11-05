# Quick Start Guide

Get started with GEO Visibility Assessment in 5 minutes!

## Step 1: Install Dependencies

```bash
cd geo_visibility
pip install -r requirements.txt
```

## Step 2: Set Up API Keys

Create a `.env` file with at least one API key:

```bash
# Copy the example
cp .env.example .env

# Edit with your favorite editor
nano .env  # or vim, code, etc.
```

Add your API key(s):
```env
OPENAI_API_KEY=sk-proj-your-key-here
PERPLEXITY_API_KEY=pplx-your-key-here
```

**Where to get keys:**
- OpenAI: https://platform.openai.com/api-keys
- Perplexity: https://www.perplexity.ai/settings/api
- Anthropic: https://console.anthropic.com/

## Step 3: Run Your First Assessment

### Quick Test (5 queries per category, ~2-3 minutes)

```bash
python -m src.main assess --max-queries 3
```

### Full Assessment (default settings, ~10-15 minutes)

```bash
python -m src.main assess
```

## Step 4: View Results

Reports are saved in the `reports/` directory:
- `report_TIMESTAMP.txt` - Human-readable console output
- `report_TIMESTAMP.md` - Markdown format
- `report_TIMESTAMP.json` - Machine-readable JSON

The report is also printed to your console!

## Common Commands

### List all available queries
```bash
python -m src.main list-queries
```

### Test only ChatGPT
```bash
python -m src.main assess --engines chatgpt
```

### Test only Gen AI business area
```bash
python -m src.main assess --business-areas gen_ai
```

### Generate query suggestions
```bash
python -m src.main suggest-queries gen_ai --count 10
```

## Understanding Your Results

### Visibility Score Scale
- **70-100**: 🟢 Excellent - Strong visibility
- **40-69**: 🟡 Good - Room for improvement
- **0-39**: 🔴 Limited - Needs attention

### Key Metrics

1. **Mention Rate**: % of queries where company is mentioned
2. **Prominence Score**: How early and prominently mentioned (0-1)
3. **Context Quality**: Quality of surrounding text (0-1)
4. **Company Rank**: Position among competitors

### Example Report Snippet

```
OVERALL VISIBILITY SCORE
----------------------------------------
[████████████░░░░░░░░░░] 45.2/100
Total Queries: 30
Total Mentions: 12
Mention Rate: 40.0%

KEY STRENGTHS
----------------------------------------
1. Strong visibility on Perplexity (58.3/100)
2. High quality context in 8 mentions (66.7%)

RECOMMENDATIONS
----------------------------------------
1. Create more authoritative content about Gen AI capabilities
2. Improve SEO for AI-powered search results
3. Publish case studies and success stories
```

## Tips for Best Results

### 1. Start Small
Begin with a small test to verify your setup:
```bash
python -m src.main assess --max-queries 2 --engines chatgpt
```

### 2. Use Query Refinement
Keep `--refine` enabled (default) to test query variations:
```bash
python -m src.main assess --refine
```

### 3. Test Strategically
Focus on one business area at a time:
```bash
# Gen AI first
python -m src.main assess --business-areas gen_ai

# Then Digital Publishing
python -m src.main assess --business-areas digital_publishing
```

### 4. Monitor Rate Limits
If you hit rate limits:
```bash
# Reduce queries
python -m src.main assess --max-queries 2

# Or test fewer engines
python -m src.main assess --engines perplexity
```

## Troubleshooting

### "No engines configured"
- Check your `.env` file exists
- Ensure at least one `*_API_KEY` is set
- Verify the key format is correct

### "ImportError: No module named..."
```bash
pip install -r requirements.txt
```

### "Rate limit exceeded"
- Wait a few minutes
- Reduce `--max-queries`
- Test one engine at a time

### "Module not found: src"
Make sure you're in the `geo_visibility` directory:
```bash
cd geo_visibility
python -m src.main assess
```

## Next Steps

1. ✅ Run initial assessment
2. 📊 Review your visibility scores
3. 📝 Read the recommendations
4. 🎯 Implement improvements
5. 🔄 Re-run assessment to track progress

## Advanced Usage

See [README.md](README.md) for:
- Custom query creation
- Adding new AI engines
- Scoring customization
- Historical tracking
- Automated monitoring

## Getting Help

- Check [README.md](README.md) for detailed documentation
- Review example reports in `reports/`
- Contact your development team for technical issues

---

**Ready to optimize your GEO visibility?** Run your first assessment now! 🚀
