import { NgModule }      from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule }   from '@angular/forms';

import { AppComponent }  from './app.component';
import {AppRoutingModule} from './app-routing.module';
import {HttpModule} from '@angular/http';
import {CurrencyService} from './services/currency.service';
import {ConverterComponent} from './converter.component';

@NgModule({
  imports:      [
    BrowserModule,
    FormsModule,
    AppRoutingModule,
    HttpModule,
  ],
  declarations: [
    AppComponent,
    ConverterComponent,
  ],
  bootstrap:    [ AppComponent ],
  providers: [ CurrencyService ]

})
export class AppModule { }
