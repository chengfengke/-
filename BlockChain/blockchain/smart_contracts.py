class IdentityManagementContract:
    def __init__(self):
        self.roles = {}

    def add_role(self, user, role):
        self.roles[user] = role

    def check_role(self, user, role):
        return self.roles.get(user) == role

class DataEncryptionContract:
    def encrypt_data(self, data, key):
        # Dummy encryption function
        return f"encrypted_{data}"

    def decrypt_data(self, encrypted_data, key):
        # Dummy decryption function
        return encrypted_data.replace("encrypted_", "")

class ClinicalTrialContract:
    def __init__(self):
        self.trials = {}

    def add_trial(self, trial_id, trial_data):
        self.trials[trial_id] = trial_data

    def get_trial(self, trial_id):
        return self.trials.get(trial_id)

class DrugRegulationContract:
    def __init__(self):
        self.regulations = {}

    def add_regulation(self, drug_id, regulation_data):
        self.regulations[drug_id] = regulation_data

    def check_compliance(self, drug_id):
        return self.regulations.get(drug_id)

class IntellectualPropertyContract:
    def __init__(self):
        self.ip_records = {}

    def register_ip(self, ip_id, ip_data):
        self.ip_records[ip_id] = ip_data

    def transfer_ip(self, ip_id, new_owner):
        if ip_id in self.ip_records:
            self.ip_records[ip_id]['owner'] = new_owner
