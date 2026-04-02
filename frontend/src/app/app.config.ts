import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';

import { routes } from './app.routes';
import { FaqDataService } from './data-access/faq-data.service';
import { RealFaqDataService } from './data-access/real-faq-data.service';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes),
    provideHttpClient(),
    {
      provide: FaqDataService,
      useClass: RealFaqDataService
    }
  ]
};
