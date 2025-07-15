export const isEmpty = (o: object) => { for (var _i in o) { return false; } return true; }
export const isNotEmpty = (o: object) => { return !isEmpty(o); }
