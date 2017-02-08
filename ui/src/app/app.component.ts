import {Component} from '@angular/core';
/**
 * Created by aanikeev on 2/7/17.
 */


@Component({
  moduleId: module.id,
  selector: 'my-app',
  styleUrls: ['./app.component.css'],
  template: `
    <h1>{{title}}</h1>
    <converter></converter>
  `,
})
export class AppComponent {
  title = 'Currency converter';
}
