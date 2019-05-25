

export default function makeParam(params) {
  let str = "";
  for (var key in params) {
      if (str != "") {
          str += "&";
      }
      str += key + "=" + encodeURIComponent(params[key]);
  }
  return str
}
