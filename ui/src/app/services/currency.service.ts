import {Injectable}    from '@angular/core';
import {Headers, Http} from '@angular/http';

import 'rxjs/add/operator/toPromise';

import {Currency} from '../models/currency';

@Injectable()
export class CurrencyService {

  private currencyUrl = 'http://127.0.0.1:8000/api/currency/';  // URL to web api
  private headers = new Headers({'Content-Type': 'application/json'});

  constructor(private http: Http) {
  }

  getSupportedCUrrencies(): Promise<string[]> {
    const url = `${this.currencyUrl}supported/`;
    return this.http.get(url, {headers: this.headers})
      .toPromise()
      .then(response => response.json() as string[])
      .catch(this.handleError);
  }

  getCurrencies(): Promise<Currency[]> {
    return this.http.get(this.currencyUrl, {headers: this.headers})
      .toPromise()
      .then(response => response.json() as Currency[])
      .catch(this.handleError);
  }

  getCurrency(base: string): Promise<Currency> {
    const url = `${this.currencyUrl}/${base}`;
    return this.http.get(url, {headers: this.headers})
      .toPromise()
      .then(response => response.json() as Currency)
      .catch(this.handleError);
  }

  convert(source: string, target: string, amount: string): Promise<string> {
    const url = `${this.currencyUrl}convert/${source}/${target}/${amount}/`;
    return this.http.get(url, {headers: this.headers})
      .toPromise()
      .then(response => response.json().result as string)
      .catch(this.handleError);
  }

  private handleError(error: any): Promise<any> {
    console.error('An error occurred', error);
    return Promise.reject(error.message || error);
  }
}
