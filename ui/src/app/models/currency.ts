export class Currency {
  base: string;
  created_timestamp: number;
  rates: Rate[];
}

export class Rate {
  base: string;
  code: string;
  rate: number;
}
