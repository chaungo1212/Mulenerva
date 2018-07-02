import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';


import { AppComponent } from './app.component';
import { SearchComponent } from './search/search.component';
import { ResultsComponent } from './results/results.component';

import { HttpModule } from '@angular/http';
import { QueryService } from './query.service';

@NgModule({
  declarations: [
    AppComponent,
    SearchComponent,
    ResultsComponent
  ],
  imports: [
    BrowserModule, HttpModule
  ],
  providers: [QueryService],
  bootstrap: [AppComponent]
})
export class AppModule { }
