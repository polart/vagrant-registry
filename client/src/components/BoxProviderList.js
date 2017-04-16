import React, {Component} from "react";
import {ListGroupItem} from "react-bootstrap";
import Moment from "moment";
import Filesize from "filesize";
import {Link} from "react-router";


export default class BoxProviderList extends Component {
  renderProviderDeleteOption = (provider) => {
    if (!this.props.canDelete) {
      return null;
    }
    return <a href="#" onClick={this.props.onDelete.bind(null, provider.provider)}>Delete</a>;
  };

  renderEditOption = (provider) => {
    if (!this.props.canEdit) {
      return null;
    }
    return <Link to={`/boxes/${this.props.boxTag}/versions/${this.props.version}/providers/${provider.provider}/edit/`}>Edit</Link>;
  };

  renderDownloadButton = (provider) => {
    if (!provider.download_url) {
      return <p>No box file</p>;
    }
    return (
        <a href={provider.download_url} className="btn btn-default">
          Download box
        </a>
    );
  };

  renderProvidersList = () => {
    if (!this.props.providers) {
      return;
    }

    return this.props.providers.map(provider => {
      return (
          <ListGroupItem
              key={provider.tag}
          >
            <h4 className="list-group-item-heading">
              {provider.provider} |&nbsp;
              <small title={Moment(provider.date_updated).format('LLL')}>
                Last updated: {Moment(provider.date_updated).fromNow()}
              </small>
            </h4>
            <p>Size: {Filesize(provider.file_size)}</p>
            {this.renderDownloadButton(provider)}
            {' '}
            {this.renderEditOption(provider)}
            {' '}
            {this.renderProviderDeleteOption(provider)}
          </ListGroupItem>
      );
    });
  };

  render() {
    return (
      <div>
        <h4>Providers</h4>
        {this.renderProvidersList()}
      </div>
    );
  }
}
