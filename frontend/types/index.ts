export interface Split {
  name: string;
  id: number;
  amount?: number;
}

export interface Expense {
  id: number;
  groupId: number;
  amount?: number;
  title: string;
  description: string;
  splits: Split[];
  timestamp: Date;
}

export interface Member {
  name: string;
  id: number;
}

export interface Group {
  name: string;
  id: number;
}
