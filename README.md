# 🌪 ISCRAM18 Twitter Hydration Pipeline

This project provides a Python-based pipeline to **hydrate tweet IDs into full tweet metadata** using the [twikit](https://github.com/misbah4064/twikit) library. It is designed to support social media data collection for disaster event analysis — specifically **Hurricane Maria** as part of the [ISCRAM 2018 dataset](https://arxiv.org/pdf/1805.05144).

---

## 📦 Project Structure

```
marcoyuuu-iscram18/
│
├── hydrate_twikit.py           # Main script to hydrate tweet IDs
├── config.ini                  # Credentials for Twitter authentication (DO NOT SHARE)
├── cookies.json                # Session cookies for twikit (auto-generated)
├── ISCRAM18_datasets/
│   └── Maria_tweet_ids.txt     # Input file with tweet IDs
├── hydrated_tweets.csv         # Output file with hydrated tweet metadata
├── failed_ids.txt              # Logs tweet IDs that failed to hydrate
├── fail_log_verbose.txt        # Detailed error log with exception traces
├── setup_and_run.bat           # Windows setup and execution script
└── requirements.txt            # Python dependencies
```

---

## 🚀 Quickstart

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/marcoyuuu-iscram18.git
cd marcoyuuu-iscram18
```

### 2. Configure credentials

Edit `config.ini`:

```ini
[X]
username = your_twitter_username
password = your_password
email = your_email@example.com
```

> 🔐 **Keep this file secure and never commit it to version control.**

### 3. Set up environment (Windows)

Run:

```bat
setup_and_run.bat
```

Or manually:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python hydrate_twikit.py
```

---

## ⚙️ Command-Line Usage

```bash
python hydrate_twikit.py --input ISCRAM18_datasets/Maria_tweet_ids.txt \
                         --output hydrated_tweets.csv \
                         --failed failed_ids.txt \
                         --limit 150 \
                         --batch-size 25
```

### Options

| Flag             | Description                              | Default                          |
|------------------|------------------------------------------|----------------------------------|
| `--input`        | Path to input file with tweet IDs        | `ISCRAM18_datasets/Maria_tweet_ids.txt` |
| `--output`       | Output file for hydrated tweet data      | `hydrated_tweets.csv`            |
| `--failed`       | File to log failed tweet IDs             | `failed_ids.txt`                 |
| `--limit`        | Max tweets to hydrate per run            | `150`                            |
| `--batch-size`   | Save tweets in batches of N              | `25`                             |

---

## 📊 Output Example

| id           | text                  | created_at | like_count | retweet_count | lang | username   |
|--------------|-----------------------|------------|------------|----------------|------|------------|
| 123456789012 | "Emergency shelters..."| 2017-09-20 | 120        | 42             | en   | redcrossPR |

---

## 🛡 Security Notice

- Credentials are stored in plaintext in `config.ini` – DO NOT push this file to GitHub.
- Session cookies are saved in `cookies.json` – also sensitive.
- A `.gitignore` file is provided to help prevent accidental commits.

---

## 📚 Dependencies

Install via `requirements.txt`:

```txt
twikit
pandas
```

You can export additional packages if needed:

```bash
pip freeze > requirements.txt
```

---

## 🧠 Motivation

This pipeline is part of a research effort analyzing the role of Twitter in crisis communication during **Hurricane Maria**. It supports data recovery for previously shared tweet IDs, ensuring that tweets can be rehydrated for analysis even after long periods.

---

## 🧪 Future Work

- Support for multiple datasets or disasters via config profiles
- Retry strategy via `tenacity`
- Jupyter notebook for exploratory data analysis
- Cross-language tweet translation (optional)

---

## 📝 License

This project is for academic research purposes. Attribution required when used in publications. Please consult the [LICENSE](LICENSE) file if included.

---

## 👤 Author

**Marco Yu**  
marco.yu@upr.edu  
University of Puerto Rico

---

## 🤝 Acknowledgments

- [twikit](https://github.com/misbah4064/twikit) – Twitter client library
- ISCRAM18 dataset

## ISCRAM Dataset
If you use the ISCRAM dataset in your research, please cite:

```bibtex
@article{firoj2018twitter,
    title={A Twitter Tale of Three Hurricanes: Harvey, Irma, and Maria},
    author={Alam, Firoj and Ofli, Ferda and Imran, Muhammad and Aupetit, Michael},
    journal={Proc. of ISCRAM, Rochester, USA},
    year={2018}
}
```