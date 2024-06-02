添加角色：


curl -X POST -H "Content-Type: application/json" -d '{"user": "alice", "role": "admin"}' http://127.0.0.1:5002/roles/add

检查角色：


curl -X GET "http://127.0.0.1:5002/roles/check?user=alice&role=admin"

注册用户：


curl -X POST -H "Content-Type: application/json" -d '{"user": "alice"}' http://127.0.0.1:5002/register


获取用户公钥：

curl -X GET "http://127.0.0.1:5002/get_public_key?user=alice"
加密数据：

curl -X POST -H "Content-Type: application/json" -d '{"user": "alice", "data": "my_secret_data"}' http://127.0.0.1:5002/encrypt

{
  "encrypted_data": "base64_encoded_encrypted_data"
}
解密数据：

使用从加密端点返回的加密数据：

curl -X POST -H "Content-Type: application/json" -d '{"user": "alice", "encrypted_data": "base64_encoded_encrypted_data"}' http://127.0.0.1:5002/decrypt
添加试验：


curl -X POST -H "Content-Type: application/json" -d '{"trial_id": "trial_1", "trial_data": "data_for_trial"}' http://127.0.0.1:5002/trial/add
获取试验：

curl -X GET "http://127.0.0.1:5002/trial/get?trial_id=trial_1"
添加药物规章：

curl -X POST -H "Content-Type: application/json" -d '{"drug_id": "drug_1", "regulation_data": "regulation_for_drug"}' http://127.0.0.1:5002/regulation/add
检查药物合规性：

curl -X GET "http://127.0.0.1:5002/regulation/check?drug_id=drug_1"
注册知识产权：

curl -X POST -H "Content-Type: application/json" -d '{"ip_id": "ip_1", "ip_data": "data_for_ip"}' http://127.0.0.1:5002/ip/register
转移知识产权：

curl -X POST -H "Content-Type: application/json" -d '{"ip_id": "ip_1", "new_owner": "bob"}' http://127.0.0.1:5002/ip/transfer
挖矿（创建新块）：

curl -X GET http://127.0.0.1:5002/mine
获取整个区块链：

curl -X GET http://127.0.0.1:5002/chain