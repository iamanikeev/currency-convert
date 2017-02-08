import {Component, OnInit} from '@angular/core';
import {CurrencyService} from './services/currency.service';
// Observable class extensions
import 'rxjs/add/observable/of';
// Observable operators
import 'rxjs/add/operator/catch';
import 'rxjs/add/operator/debounceTime';
import 'rxjs/add/operator/distinctUntilChanged';
import {Subject} from 'rxjs/Subject';
import {Observable} from 'rxjs/Observable';


@Component({
  moduleId: module.id,
  selector: 'converter',
  styleUrls: ['./converter.component.css'],
  templateUrl: './converter.component.html',
})
export class ConverterComponent implements OnInit {

  supportedSources: string[];
  supportedTargets: string[];
  sourceCurrency: string;
  targetCurrency: string;
  amount: string;
  result: string;

  constructor(private currencyService: CurrencyService) {
  }

  ngOnInit(): void {
    this.currencyService.getSupportedCUrrencies()
      .then(currencies => this.supportedSources = currencies);
  }

  filterTargetsCurrencies(code: string): void {
    const currencies = this.supportedSources;
    this.supportedTargets = currencies.filter(v => v !== code);
  }

  convert(amount: string): void {
    this.currencyService.convert(this.sourceCurrency, this.targetCurrency, amount)
      .then(result => this.result = result)
      .catch(error => alert(error));
  }
}
