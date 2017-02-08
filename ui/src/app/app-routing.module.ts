import { NgModule }             from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import {ConverterComponent} from './converter.component';

const routes: Routes = [
  { path: 'converter',  component: ConverterComponent },
];
@NgModule({
  imports: [ RouterModule.forRoot(routes) ],
  exports: [ RouterModule ]
})

export class AppRoutingModule {}
