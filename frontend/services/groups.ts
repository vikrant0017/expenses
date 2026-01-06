const BASE_URL = "http://192.168.0.136:3000";

export const getGroupMembers = async (groupId: number) => {
  const res = await fetch(`${BASE_URL}/groups/${groupId}/members`);
  const jsonRes = await res.json();
  return jsonRes;
};

export const getGroups = async () => {
  const res = await fetch(`${BASE_URL}/groups`);
  const jsonRes = await res.json();
  return jsonRes;
};

export const getGroup = async (groupId: number) => {
  const res = await fetch(`${BASE_URL}/groups/${groupId}`);
  const jsonRes = await res.json();
  return jsonRes;
};
