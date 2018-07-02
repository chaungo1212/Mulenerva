import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { AppComponent } from './app.component';
import { QueryService } from './query.service';
import { ButtonsComponent } from './buttons/buttons.component';

@NgModule({
  declarations: [
    AppComponent,
    ButtonsComponent
  ],
  imports: [
    BrowserModule
  ],
  providers: [QueryService],
  bootstrap: [AppComponent]
})
export class AppModule { }
