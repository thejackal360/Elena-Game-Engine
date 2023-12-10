function Temperature_Controller_Part_II_subjs(topic, val) {
    switch (topic) {
        
        case Temperature_Controller_Part_IIExperiment0Topic:
            Experiment0(val);
            break;
        
        case Temperature_Controller_Part_IIArtGen0Topic:
            ArtGen0(val);
            break;
        
        default: /* do nothing */;
    }
}