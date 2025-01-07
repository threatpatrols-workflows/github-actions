
import vt
import time
import datetime

from threatpatrols.exceptions import ThreatPatrolsException

ANALYSIS_RESUBMISSION_TTL = (4 * 3600)


class VirustotalAnalysisBase:

    api_key: str
    analysis_resubmission_ttl: int

    def __init__(self, api_key: str, analysis_resubmission_ttl=ANALYSIS_RESUBMISSION_TTL):
        if not api_key:
            raise ThreatPatrolsException("Cannot use Virustotal without an API key, please provide.")
        self.api_key = api_key
        self.analysis_resubmission_ttl = analysis_resubmission_ttl

    def _wait_for_completion(self, analysis_id, interval_seconds=15, max_checks=20):
        with vt.Client(self.api_key) as client:
            checks_count = 0
            while True:
                analysis = client.get_object("/analyses/{}", analysis_id)
                checks_count += 1
                if checks_count >= max_checks:
                    raise ThreatPatrolsException(f"Timeout waiting for submission completion {analysis_id=}")
                if analysis.status == "completed":
                    return
                time.sleep(interval_seconds)

        raise ThreatPatrolsException(f"Unexpected condition in _wait_for_completion()")


class VirustotalUrlAnalysis(VirustotalAnalysisBase):

    def submit_wait_for_analysis(self, url: str, force_resubmission: bool = False):
        object_id = self.submit(url=url, wait_for_completion=True, force_resubmission=force_resubmission)
        return self.get_analysis(object_id=object_id)

    def submit(self, url: str, wait_for_completion: bool = False, force_resubmission: bool = False) -> str:
        if force_resubmission is False:
            existing = self._get_existing_analysis(url=url)
            if existing:
                seconds_ago = time.time() - existing.get("attributes").get("last_analysis_date")
                if seconds_ago < self.analysis_resubmission_ttl:
                    return existing.get("id")

        with vt.Client(self.api_key) as client:
            submission = client.scan_url(url, wait_for_completion=wait_for_completion)
            object_id = str(submission.id).split("-")[1]
        return object_id

    def get_analysis(self, object_id: str):
        with vt.Client(self.api_key) as client:
            analysis = client.get_data("/urls/{}", object_id)
        return analysis

    def _get_existing_analysis(self, url: str):
        if not url.startswith("http"):
            raise ThreatPatrolsException(f"Invalid URL value supplied.")

        with vt.Client(self.api_key) as client:
            try:
                analysis = client.get_data(f"/urls/{vt.url_id(url)}")
            except vt.error.APIError:
                return None
        if analysis and analysis.get("attributes").get("sha256"):
            return analysis
        return None


class VirustotalHashAnalysis(VirustotalAnalysisBase):

    def submit_wait_for_analysis(self, hash_value: str, force_resubmission: bool = False):
        self.submit(
            hash_value=hash_value, wait_for_completion=True, force_resubmission=force_resubmission
        )
        return self._get_existing_analysis(hash_value=hash_value)

    def submit(self, hash_value: str, wait_for_completion=False, force_resubmission=False):
        if force_resubmission is False:
            existing = self._get_existing_analysis(hash_value=hash_value)
            if existing:
                seconds_ago = time.time() - existing.get("attributes").get("last_analysis_date")
                if seconds_ago < self.analysis_resubmission_ttl:
                    return existing.get("id")

        with vt.Client(self.api_key) as client:
            submission = client.post("/files/{}/analyse", hash_value)
            if not submission:
                raise ThreatPatrolsException("Failed to submit file hash for submission, try again?")
            analysis_id = submission.json().get("data", {}).get("id")
            if analysis_id and wait_for_completion:
                self._wait_for_completion(analysis_id=analysis_id)
        return hash_value

    def get_analysis(self, object_id: str):
        return self._get_existing_analysis(hash_value=object_id)

    def _get_existing_analysis(self, hash_value: str):
        if hash_value and len(hash_value) != 32 and len(hash_value) != 40 and len(hash_value) != 64:
            raise ThreatPatrolsException(f"Invalid hash value supplied.")

        with vt.Client(self.api_key) as client:
            try:
                analysis = client.get_data(f"/files/{hash_value}")
            except vt.error.APIError:
                return None
        if analysis and analysis.get("attributes").get("sha256"):
            return analysis
        return None
