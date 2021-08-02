# TFM
This repository contains the code used in my MSc Final Thesis, finished in 2018. It has been uploaded on demand.

## MSc Original Thesis

The complete thesis can be found in the [idUS repository](https://idus.us.es/handle/11441/81096) by the University of Seville. Please notice that the original text is in Spanish.

## Modules

Code has been uploaded as it is, without any further modification.

Directory structure is as follows:

- First level specifies the logical entity where the application or script is executed
  - Raspberry Pi device, data collecting machine, processing machine.
  - There's also a specific block for Docker files defined.

- Second level (if exists), implies a different program or logical separation within the first level.
  - Raspberry Pi: Radio Rx, Data Collector, ...
  - Docker: FIWARE, MySQL, ...
  - ...

## Execution

Notice that to be able to execute appropriately this code and get the full system to work together, you may need to follow the instructions available in the thesis document.

Also, several conectivity IP Addresses and so forth may need to be updated to make it work on your deployment.

### Data Collection Authentication

Facebook authentication data has been removed from `Data Collection > Facebook > FBCollector.py`:

```
PAGE_ID = ''
PAGE_TOKEN = ''
```

You will need to update them to connect to your own Facebook page.

## License

Feel free to base your work on this project, attending to the MIT License applied. Any work based on this thesis or code must quote the original source.

This project is shared under a [MIT License](LICENSE). Please refer to the [following link](https://choosealicense.com/licenses/mit/) to have a brief view of what does it imply.